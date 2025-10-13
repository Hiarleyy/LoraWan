---
AutoNoteMover: disable
Status: active
Autor: Beatriz Pestana Teixeira || Marcus Vinicius da Silva Barros Fioravante ||  Débora Meyhofer Ferreira
Ano: "2025"
Keywords: lorawan | lora | snr | packet-loss
Reference: "[[LORA X NS-3 POTÊNCIA DO SINAL, SNR, PERDA DEPACOTE.pdf]]"
tags:
  - lorawan
  - lora
  - snr
  - packet-loss
data: 2025-10-08T10:20:00
---

---
*Síntese*: 

Esse trabalho se propõe não apenas a entender o funcionamento da tecnologia LoRa® mas também em comparar o desempenho de funcionamento de um link ponto a ponto na prática com o resultado de simulação do mesmo cenário. O simulador utilizado é o NS-3 (Network Simulator 3) e o hardware utilizado é o ESP32 da Heltec, comparando em parâmetros como relação sinal ruído, alcance e perda de pacote. Foram utilizados diversos cenários, tanto para a simulação quanto para o experimento prático. O simulador demonstrou resultados bem próximos aos reais, exceto na situação onde a topologia do terreno não permitiu linha de visada. PALAVRAS-CHAVE: LoRa, comunicação, LPWAN, NS-3, prova de desempenho, perda de pacote, SNR, potência do sinal, comparação. ABSTRACT This work proposes not only to understand how LoRa® technology works, but also to compare the performance of a point-to-point link in practice with the simulation result of the same scenario. The simulator used is the NS-3 (Network Simulator 3) and the hardware used is the ESP32 from Heltec, comparing parameters such as signal-to-noise ratio, range and packet loss. Several scenarios were used, both for the simulation and for the practical experiment. The simulator showed results very close to the real ones, except in the situation where the terrain topology did not allow line of sight. KEYWORDS: LoRa, communication, LPWAN, NS-3, performance test, packet loss, SNR, Signal strength, potency comparison. INTRODUÇÃO 

---

# Tópicos principais LoraWan

## Spreading Factor

LoRa é baseado na tecnologia Chirp Spread Spectrum (CSS), onde os chirps (também conhecidos como símbolos) são os portadores de dados.

O fator de espalhamento controla a taxa de chirp e, portanto, a velocidade de transmissão de dados. **Fatores de espalhamento mais baixos** significam **chirps mais rápidos** e, portanto, uma **taxa de transmissão de dados mais alta** . Para cada aumento no fator de espalhamento, a taxa de varredura do chirp é reduzida pela metade e, portanto, a taxa de transmissão de dados é reduzida pela metade.

Para uma explicação visual, assista a [este vídeo](https://www.youtube.com/watch?v=dxYY097QNs0) sobre sons LoRa.

Fatores de espalhamento mais baixos reduzem o alcance das transmissões LoRa, pois reduzem o ganho de processamento e aumentam a taxa de bits. Alterar o fator de espalhamento permite que a rede aumente ou diminua a taxa de dados para cada dispositivo final, em detrimento do alcance.

A rede também utiliza fatores de espalhamento para controlar o congestionamento. Os fatores de espalhamento são ortogonais, de modo que sinais modulados com diferentes fatores de espalhamento e transmitidos no mesmo canal de frequência ao mesmo tempo não interferem entre si.

## Taxa de dados
Comparado a um fator de espalhamento mais alto, um fator de espalhamento mais baixo proporciona uma taxa de bits mais alta para uma largura de banda e taxa de codificação fixas. Por exemplo, o SF7 proporciona uma taxa de bits mais alta que o SF12.

Dobrar a largura de banda também dobra a taxa de bits para um fator de espalhamento fixo e a taxa de codificação.

A tabela a seguir apresenta taxas de bits calculadas com SF7 e Taxa de Codificação (CR) = 1 para larguras de banda de 125, 250 e 500 kHz.

## Questões

#### 1. Qual fator de espalhamento fornece a maior sensibilidade do receptor?
- SF9
- SF10
- SF11
- **SF12**
#### 2. Qual fator de espalhamento fornece a maior taxa de bits?
- **SF7**
- SF8
- SF9
- SF10
#### 3. Qual fator de dispersão proporciona a maior duração de bateria para um dispositivo final?

- **SF7**
- SF8
- SF9
- SF10

	_Fatores de espalhamento mais baixos proporcionam taxas de bits mais altas, resultando em um TOA mais curto. Um TOA mais curto resulta em maior vida útil da bateria, pois o transceptor de rádio fica ativo por um período mais curto._

#### 4. Para a mesma quantidade de dados e largura de banda, qual fator de dispersão resulta no maior tempo no ar?
- SF7
- SF8
- SF9
- **SF10**
---
# Arquitetura LoraWan

A arquitetura de rede LoraWan é implantada em uma topologia de rede de estrela, onde diversos **gateways** encaminham mensagens para os **endDevices** para um servidor central da rede. ==Os gateways são conectados ao servidor via conexão IP padrão== e atuam como uma ponte transparente, convertendo os pacotes RF em pacotes IP e vice-versa conforme a figura: 
![[Pasted image 20251013105236.png]]

A comunicação sem fio aproveita as características de longo alcance da camada física para permitir um link de salto único, do **endDevice** para um ou vários **gateways**. Todos os modos são capazes de realizar uma comunicação bidirecional, com suporte para grupos de endereçamento **multicast** (método de transmissão de um pacote de dados para múltiplos destinos ao mesmo tempo), a fim de fazer o uso eficiente do espectro durante tarefas como atualizações do Firmware FOTA. Os dispositivos lora são categorizados por classe e são definidos em 3 tipos de classe diferentes separados entre A, B e C.

### 1. Classe A

- A classe A tem como particularidade a ==espera de uma resposta de um período== de 2 segundos após o envio, essa classe é a que menos consome energia dentre as 3 classes, pois apenas recebe a informação quando a mensagem chega com sucesso em um **gateway**

![[Pasted image 20251013110200.png]]
### 2. Classe B
- A classe B tem a janela de recebimento de dados configurada, o dispositivo recebe um despertar do gateway em períodos pré-determinados e  configurados através de mensagens de **beacon** emitidas pelo **gateway**, desta forma há garantia de que o dispositivo está apto para receber os pacotes,==portanto se classifica como uma verificação para evitar perca de pacotes para um **endDevice** que está inativo==.
![[Pasted image 20251013110807.png]]

### 3. Classe C

- A classe C tem o maior período de recepção entre as classes de dispositivos, a sua janela de recepção é continua e fechada em caso de transmissão.
![[Pasted image 20251013110943.png]]

----

# Segurança da Rede

- A rede LoraWan utiliza de duas camadas de proteção para garantir a segurança da rede, a primeira visa garantir a autenticidade do nó na rede, e a segunda garante que o operador da rede não tenha acesso aos dados do aplicativo do uso final. Para isso, é utilizado uma encriptação do tipo AES3(advanced encryption standard) em trocas de chave de identificador IEEE EUI64 (formato de identificador exclusivo extendido de 64 bits) Existem compensações em cada escolha de tecnologia, exeto os recursos de LoraWan. Na arquitetura de rede, classe de dispositivos, segurança, escalabilidade para capacidade e a otimização para mobilidade onde aborda a mais ampla variedade de aplicações IoT em potencial.

