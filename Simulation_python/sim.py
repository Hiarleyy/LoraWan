import numpy as np
import pandas as pd
from collections import defaultdict, Counter
import matplotlib.pyplot as plt

# Parâmetros da simulação baseados no arquivo ns-3
N_DEVICES = 100  # Número de end devices
N_GATEWAYS = 5   # Número de gateways
SIDE_LENGTH = 1000  # Área quadrada em metros
TX_POWER = 14.0  # dBm
PL0 = 40.0       # Path loss referência a 1m
N_PATHLOSS = 3.0 # Expoente path loss
NOISE_FIGURE = 6.0  # dB
BANDWIDTH = 125e3  # Hz (SF12/BW125)
NOISE_FLOOR = -174 + 10*np.log10(BANDWIDTH) + NOISE_FIGURE  # dBm
SIM_TIME = 604800  # 1 semana em segundos
APP_PERIOD = 14400  # 2 horas por pacote
PAQUETES_ENV = int(SIM_TIME / APP_PERIOD)  # ~42 pacotes por device

# Posições fixas dos gateways (como no código ns-3)
GW_POS = np.array([
    [0, 0],
    [750, -750],
    [-750, 750],
    [750, 750],
    [-750, -750]
])

def calculate_pathloss(distance):
    """Path loss log-distance: PL = PL0 + 10*n*log10(d/1)"""
    if distance == 0:
        return 0
    return PL0 + 10 * N_PATHLOSS * np.log10(distance)

def calculate_sinr(tx_pos, gw_pos, interference=3.0):
    """SINR = RxPower - Noise - Interference (simplificado para LoRa)"""
    dist = np.linalg.norm(tx_pos - gw_pos)
    pathloss = calculate_pathloss(dist)
    rx_power = TX_POWER - pathloss
    sinr = rx_power - NOISE_FLOOR - interference
    return max(sinr, -20)  # SINR mínimo -20dB

def sf_from_sinr(sinr):
    """Mapeia SINR para SF baseado em thresholds ADR típicos LoRaWAN"""
    if sinr > 15: return 7
    elif sinr > 10: return 8
    elif sinr > 5: return 9
    elif sinr > 0: return 10
    elif sinr > -5: return 11
    else: return 12

def simulate_packets(pdr):
    """Simula pacotes recebidos baseado em PDR (probabilidade de entrega)"""
    pac_enviados = PAQUETES_ENV
    pac_recebidos = np.random.binomial(pac_enviados, pdr / 100)
    return pac_enviados, pac_recebidos

def simulate_delay(sf):
    """Delay aproximado baseado em SF (tempo no ar + ACK, simplificado)"""
    airtime = {7: 0.05, 8: 0.07, 9: 0.11, 10: 0.18, 11: 0.34, 12: 0.61}  # segundos
    return airtime.get(sf, 0.61) * 1000 + np.random.exponential(50)  # ms + variação

# Gerar posições aleatórias dos devices
np.random.seed(42)
device_pos = np.random.uniform(0, SIDE_LENGTH, (N_DEVICES, 2))

# Simulação principal
results = []
sf_counts = Counter()

for dev_id in range(N_DEVICES):
    tx_pos = device_pos[dev_id]
    best_gw_idx = np.argmin([np.linalg.norm(tx_pos - gw) for gw in GW_POS])
    best_dist = np.linalg.norm(tx_pos - GW_POS[best_gw_idx])
    
    sinr_db = calculate_sinr(tx_pos, GW_POS[best_gw_idx])
    rx_power = TX_POWER - calculate_pathloss(best_dist)  # Potência recebida
    sf = sf_from_sinr(sinr_db)
    sf_counts[sf] += 1
    
    # PDR baseado em SINR (threshold típico LoRa)
    pdr = min(100, max(0, 20 + sinr_db * 5))  # ~100% se SINR>16dB
    pac_env, pac_rec = simulate_packets(pdr)
    delay_ms = simulate_delay(sf)
    
    results.append({
        'Device': dev_id,
        'Dist_GW_m': best_dist,
        'SINR_dB': sinr_db,
        'RxPower_dBm': rx_power,
        'SF': sf,
        'Pac_Env': pac_env,
        'Pac_Rec': pac_rec,
        'PDR_%': pdr,
        'Delay_ms': delay_ms
    })

# DataFrame e estatísticas
df = pd.DataFrame(results)

## Estatísticas Globais
print("=== PREVISÕES LoRaWAN (semelhante a LoraWanNewSimulation.cc) ===")
print(f"SINR médio: {df['SINR_dB'].mean():.2f} dB")
print(f"Potência recebida média: {df['RxPower_dBm'].mean():.2f} dBm")
print(f"Total pacotes enviados: {df['Pac_Env'].sum()}")
print(f"Total pacotes recebidos: {df['Pac_Rec'].sum()}")
print(f"PDR médio: {df['PDR_%'].mean():.2f}%")
print(f"Delay médio: {df['Delay_ms'].mean():.2f} ms")
print("\nPrevalência de Spreading Factors:")
for sf, count in sf_counts.most_common():
    perc = 100 * count / N_DEVICES
    print(f"  SF{sf}: {count} devices ({perc:.1f}%)")

## Estatísticas Detalhadas por Variável
print("\n" + "="*60)
print("ANÁLISE DETALHADA DAS VARIÁVEIS")
print("="*60)

# Distância ao Gateway
print("\nDISTÂNCIA AO GATEWAY (m):")
print(f"   Mínima:  {df['Dist_GW_m'].min():.2f} m")
print(f"   Máxima:  {df['Dist_GW_m'].max():.2f} m")
print(f"   Média:   {df['Dist_GW_m'].mean():.2f} m")
print(f"   Mediana: {df['Dist_GW_m'].median():.2f} m")
print(f"   Desvio:  {df['Dist_GW_m'].std():.2f} m")

# SINR
print("\nSINR (dB):")
print(f"   Mínimo:  {df['SINR_dB'].min():.2f} dB")
print(f"   Máximo:  {df['SINR_dB'].max():.2f} dB")
print(f"   Média:   {df['SINR_dB'].mean():.2f} dB")
print(f"   Mediana: {df['SINR_dB'].median():.2f} dB")
print(f"   Desvio:  {df['SINR_dB'].std():.2f} dB")

# Potência Recebida
print("\nPOTÊNCIA RECEBIDA (dBm):")
print(f"   Mínima:  {df['RxPower_dBm'].min():.2f} dBm")
print(f"   Máxima:  {df['RxPower_dBm'].max():.2f} dBm")
print(f"   Média:   {df['RxPower_dBm'].mean():.2f} dBm")
print(f"   Mediana: {df['RxPower_dBm'].median():.2f} dBm")
print(f"   Desvio:  {df['RxPower_dBm'].std():.2f} dBm")

# PDR
print("\nPDR - PACKET DELIVERY RATIO (%):")
print(f"   Mínimo:  {df['PDR_%'].min():.2f}%")
print(f"   Máximo:  {df['PDR_%'].max():.2f}%")
print(f"   Média:   {df['PDR_%'].mean():.2f}%")
print(f"   Mediana: {df['PDR_%'].median():.2f}%")
print(f"   Desvio:  {df['PDR_%'].std():.2f}%")

# Delay
print("\nDELAY (ms):")
print(f"   Mínimo:  {df['Delay_ms'].min():.2f} ms")
print(f"   Máximo:  {df['Delay_ms'].max():.2f} ms")
print(f"   Média:   {df['Delay_ms'].mean():.2f} ms")
print(f"   Mediana: {df['Delay_ms'].median():.2f} ms")
print(f"   Desvio:  {df['Delay_ms'].std():.2f} ms")

# Análise de correlações
print("\nCORRELAÇÕES ENTRE VARIÁVEIS:")
corr_dist_sinr = df['Dist_GW_m'].corr(df['SINR_dB'])
corr_sinr_pdr = df['SINR_dB'].corr(df['PDR_%'])
corr_dist_pdr = df['Dist_GW_m'].corr(df['PDR_%'])
corr_sf_delay = df['SF'].corr(df['Delay_ms'])
print(f"   Distância vs SINR:  {corr_dist_sinr:.3f}")
print(f"   SINR vs PDR:        {corr_sinr_pdr:.3f}")
print(f"   Distância vs PDR:   {corr_dist_pdr:.3f}")
print(f"   SF vs Delay:        {corr_sf_delay:.3f}")

## Salvar resultados (como sinrdata.csv no ns-3)
df.to_csv('lora_predicoes.csv', index=False)
print("\nDados salvos em 'lora_predicoes.csv'")

# ============================================================
# GRÁFICOS DE ANÁLISE COMPLETA
# ============================================================
fig, axes = plt.subplots(3, 2, figsize=(14, 15))
fig.suptitle('Análise Completa da Simulação LoRaWAN', fontsize=16, fontweight='bold')

# 1. Prevalência de SF
ax1 = axes[0, 0]
sf_counts_df = pd.DataFrame.from_dict(sf_counts, orient='index', columns=['Count']).sort_index()
colors_sf = plt.cm.viridis(np.linspace(0.2, 0.8, len(sf_counts_df)))
ax1.bar(sf_counts_df.index, sf_counts_df['Count'], color=colors_sf)
ax1.set_xlabel('Spreading Factor')
ax1.set_ylabel('Número de Devices')
ax1.set_title('Prevalência de Spreading Factors')
for i, (sf, row) in enumerate(sf_counts_df.iterrows()):
    ax1.annotate(f'{row["Count"]}', (sf, row['Count']), ha='center', va='bottom')

# 2. Histograma de Distâncias
ax2 = axes[0, 1]
ax2.hist(df['Dist_GW_m'], bins=20, color='steelblue', edgecolor='white', alpha=0.8)
ax2.axvline(df['Dist_GW_m'].mean(), color='red', linestyle='--', label=f'Média: {df["Dist_GW_m"].mean():.1f}m')
ax2.set_xlabel('Distância ao Gateway (m)')
ax2.set_ylabel('Frequência')
ax2.set_title('Distribuição de Distâncias ao Gateway')
ax2.legend()

# 3. SINR vs Distância
ax3 = axes[1, 0]
scatter1 = ax3.scatter(df['Dist_GW_m'], df['SINR_dB'], c=df['SF'], cmap='plasma', alpha=0.7, s=50)
ax3.set_xlabel('Distância ao Gateway (m)')
ax3.set_ylabel('SINR (dB)')
ax3.set_title('SINR vs Distância (colorido por SF)')
cbar1 = plt.colorbar(scatter1, ax=ax3)
cbar1.set_label('SF')

# 4. PDR vs SINR
ax4 = axes[1, 1]
scatter2 = ax4.scatter(df['SINR_dB'], df['PDR_%'], c=df['Dist_GW_m'], cmap='coolwarm', alpha=0.7, s=50)
ax4.set_xlabel('SINR (dB)')
ax4.set_ylabel('PDR (%)')
ax4.set_title('PDR vs SINR (colorido por distância)')
cbar2 = plt.colorbar(scatter2, ax=ax4)
cbar2.set_label('Distância (m)')

# 5. Histograma de Potência Recebida
ax5 = axes[2, 0]
ax5.hist(df['RxPower_dBm'], bins=20, color='darkorange', edgecolor='white', alpha=0.8)
ax5.axvline(df['RxPower_dBm'].mean(), color='red', linestyle='--', label=f'Média: {df["RxPower_dBm"].mean():.1f} dBm')
ax5.set_xlabel('Potência Recebida (dBm)')
ax5.set_ylabel('Frequência')
ax5.set_title('Distribuição da Potência Recebida')
ax5.legend()

# 6. Boxplot de Delay por SF
ax6 = axes[2, 1]
df_grouped = [df[df['SF'] == sf]['Delay_ms'].values for sf in sorted(df['SF'].unique())]
bp = ax6.boxplot(df_grouped, labels=[f'SF{sf}' for sf in sorted(df['SF'].unique())], patch_artist=True)
colors_box = plt.cm.viridis(np.linspace(0.2, 0.8, len(df_grouped)))
for patch, color in zip(bp['boxes'], colors_box):
    patch.set_facecolor(color)
ax6.set_xlabel('Spreading Factor')
ax6.set_ylabel('Delay (ms)')
ax6.set_title('Distribuição de Delay por SF')

plt.tight_layout()
plt.savefig('analise_completa.png', dpi=150, bbox_inches='tight')
print("Gráfico completo salvo em 'analise_completa.png'")
plt.show()

# Gráfico extra: Mapa de posições dos devices
fig2, ax = plt.subplots(figsize=(10, 10))
scatter_map = ax.scatter(device_pos[:, 0], device_pos[:, 1], c=df['PDR_%'], cmap='RdYlGn', 
                          s=80, alpha=0.8, edgecolors='black', linewidth=0.5)
ax.scatter(GW_POS[:, 0], GW_POS[:, 1], c='blue', marker='^', s=300, label='Gateways', edgecolors='black', linewidth=2)
ax.set_xlabel('Posição X (m)')
ax.set_ylabel('Posição Y (m)')
ax.set_title('Mapa de Devices e Gateways (colorido por PDR)')
ax.legend(loc='upper right')
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)
cbar = plt.colorbar(scatter_map, ax=ax)
cbar.set_label('PDR (%)')
plt.savefig('mapa_devices.png', dpi=150, bbox_inches='tight')
print("Mapa salvo em 'mapa_devices.png'")
plt.show()
