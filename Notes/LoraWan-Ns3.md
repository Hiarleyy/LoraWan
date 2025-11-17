Este módulo contém uma série de classes e exemplos destinados a modelar a modulação e a tecnologia de acesso ao meio de uma rede LoRaWAN. Graças a um modelo de camada física subjacente simples e às regulamentações impostas ao tráfego nas bandas não licenciadas em que esta tecnologia opera, este módulo pode suportar simulações com um grande número de dispositivos que acessam o canal sem fio com pouca frequência.

As seções seguintes desta documentação descrevem primeiro como a tecnologia funciona e, em seguida, como ela foi traduzida em um sistema de classes para simular um sistema LoRaWAN.

## 18.1. Tecnologia [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#technology "Link para este cabeçalho")

LoRaWAN é uma tecnologia de Rede de Longo Alcance de Baixa Potência (LPWAN) baseada na modulação LoRa. Essa tecnologia permite que um grande número de dispositivos se comunique sem fio em longas distâncias (da ordem de 5 a 15 km, dependendo do ambiente de propagação) com baixas taxas de dados. O cenário típico em que essa tecnologia é esperada é o de uma rede IoT, onde os dispositivos precisam se comunicar de forma esparsa e necessitam apenas de cargas úteis curtas para transmitir informações provenientes, geralmente, de um sensor.

### 18.1.1. LoRa [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#lora "Link para este cabeçalho")

A base do LoRaWAN é a modulação proprietária de longo alcance (LoRa), pertencente à Semtech. Essa modulação, baseada em Chirp Spread Spectrum (CSS), espalha um sinal em uma determinada banda utilizando um sinal chirp que varre a largura de banda disponível linearmente.

Um dos parâmetros-chave da modulação é o Fator de Espalhamento (SF): esse valor, que varia de 7 a 12, expressa o quanto um pacote é espalhado no tempo (ou seja, quanto tempo leva para um chirp completar uma varredura completa da largura de banda disponível). Transmissões com um SF baixo precisam de um Tempo de Transmissão (ToA) menor (considerando a mesma largura de banda) do que pacotes com valores de SF próximos a 12. A vantagem de usar SFs mais altos reside no aumento da sensibilidade do receptor: por exemplo, uma transmissão com SF 7 que não pode ser detectada por um receptor LoRa pode ser demodulada corretamente se realizada com SF 12. Outra característica fundamental da modulação é a quase ortogonalidade entre transmissões com diferentes valores de SF: mesmo que dois pacotes se sobreponham no tempo, um receptor ainda pode ser capaz de demodular um dos pacotes, desde que eles usem SFs diferentes e que certas restrições sobre a potência recíproca sejam respeitadas.

Mais detalhes sobre como a modulação funciona podem ser encontrados em [[semtech2015modulation]](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#semtech2015modulation) (um documento oficial que explica a modulação) e em [[knight2016reversing]](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#knight2016reversing) (uma engenharia reversa da modulação feita por Matt Knight).

### 18.1.2. LoRaWAN [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#lorawan "Link para este cabeçalho")

A LoRa Alliance definiu pela primeira vez o padrão LoRaWAN em [[lorawanstandard]](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#lorawanstandard) , com o objetivo de criar um esquema de acesso ao meio e um conjunto de políticas de gerenciamento de rede que aproveitem as propriedades da modulação para alcançar um bom desempenho de rede a um custo baixo na complexidade dos dispositivos.

A topologia de uma rede LoRaWAN é representada na figura [Topologia da arquitetura LoRaWAN](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#lorawan-topology) , onde as linhas tracejadas representam um enlace sem fio LoRa, enquanto as linhas contínuas representam outros tipos de conexões de alta taxa de transferência e alta confiabilidade. Pode-se observar que existem três tipos de dispositivos em uma rede LoRaWAN: Dispositivos Finais (EDs), Gateways (GWs) e um Servidor de Rede (NS). Os Dispositivos Finais são nós básicos da rede: geralmente de baixo custo, possuem capacidades computacionais limitadas e são normalmente alimentados por bateria. Os Gateways são dispositivos de alta gama, alimentados pela rede elétrica, responsáveis ​​por coletar os dados transmitidos pelos Dispositivos Finais, utilizando a modulação LoRa. Após um pacote ser recebido corretamente, ele é encaminhado para o Servidor de Rede por meio de um enlace de alta confiabilidade e velocidade. O Servidor de Rede funciona como um coletor de dados provenientes de todos os dispositivos e como um controlador da rede, podendo utilizar comandos MAC para alterar as configurações de transmissão nos Dispositivos Finais.

Os dispositivos finais do tipo mais básico são definidos como dispositivos de Classe A e são atualmente o único tipo de dispositivo suportado por este módulo. Os dispositivos de Classe A realizam a transmissão de forma totalmente assíncrona e abrem duas janelas de recepção de duração fixa após cada transmissão para permitir que o Servidor de Rede transmita confirmações ou comandos MAC.

Outra característica importante do padrão é que ele foi definido para operar em bandas não licenciadas em diversas regiões, que geralmente sujeitam os transmissores a regulamentações sobre ciclo de trabalho. Esse fato será explicado com mais detalhes na seção sobre o modelo da camada MAC deste documento.

![_images/lorawan-topology.png](https://signetlabdei.github.io/lorawan/models/build/html/_images/lorawan-topology.png)

Topologia da arquitetura LoRaWAN. [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#id8 "Link para esta imagem")

## 18.2. Projeto do módulo [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#module-design "Link para este cabeçalho")

Este módulo compreende dois modelos principais: um para a camada física (PHY) LoRa, que precisa representar os chips LoRa e o comportamento das transmissões LoRa, e outro para a camada MAC LoRaWAN, que precisa se comportar de acordo com as especificações oficiais.

Para representar esses dois modelos, o módulo apresenta duas classes genéricas `LoraPhy`e `LorawanMac`básicas. Essas classes são então estendidas por classes que modelam as peculiaridades dos dois dispositivos de rede sem fio: o Dispositivo Final (ED) e o Gateway (GW). Assim, as camadas PHY podem ser modeladas pelo uso das classes `EndDisplay` `EndDeviceLoraPhy`e `Gateway` `GatewayLoraPhy`, enquanto objetos das classes ` EndDisplay` `EndDeviceLorawanMac`, `Gateway` `ClassAEndDeviceLorawanMac`e `Gateway` `GatewayLorawanMac` são usados ​​para representar a camada MAC. Um `NetworkServer`aplicativo também pode ser instalado em um nó para administrar a rede sem fio por meio do aplicativo de encaminhamento do GW, `NetworkServer` `Forwarder`, que aproveita os recursos de comunicação LoRa do gateway para encaminhar os pacotes do Servidor de Rede para os Dispositivos Finais.

### 18.2.1. Modelo da camada física [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#phy-layer-model "Link para este cabeçalho")

O modelo para a camada física (PHY) precisa levar em consideração os dois fatores-chave do LoRa, sensibilidade e ortogonalidade, para determinar se uma transmissão foi recebida corretamente ou não. Além disso, também precisa estar ciente de como os chips que implementam a modulação funcionam e de sua arquitetura.

#### 18.2.1.1. Modelo de ligação [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#link-model "Link para este cabeçalho")

O modelo de enlace leva em consideração três componentes principais para determinar o desempenho de uma transmissão LoRa:

- Dados sobre a sensibilidade do dispositivo obtidos nas fichas técnicas do mesmo;
    
- Um modelo para contabilizar a interferência entre diferentes transmissões LoRa;
    
- Uma série de suposições referentes a este modelo de interferência.
    

Nesta seção, descreveremos cada parte do modelo com foco especial em sua implementação no código.

A `LoraChannel`classe é usada para interconectar as camadas PHY LoRa de todos os dispositivos que desejam se comunicar usando essa tecnologia. A classe mantém uma lista das camadas PHY conectadas e as notifica sobre transmissões recebidas, seguindo o mesmo paradigma de outras `Channel`classes no _ns-3_ .

As camadas PHY conectadas ao canal expõem um `StartReceive` método público que permite ao canal iniciar a recepção em uma determinada camada PHY. Nesse ponto, essas classes PHY dependem de um `LoraInterferenceHelper`objeto para rastrear todos os pacotes recebidos, tanto os potencialmente desejáveis ​​quanto os de interferência. Assim que o canal notifica a camada PHY sobre o pacote recebido, a camada PHY informa seu `LoraInterferenceHelper`próprio objeto sobre a transmissão recebida. Depois disso, se uma camada PHY atender a certos pré-requisitos, ela poderá se conectar ao pacote recebido para recepção. Para isso:

1. O receptor deve estar ocioso (em estado de espera) quando a `StartReceive` função for chamada;
    
2. A potência de recepção do pacote deve estar acima de um limite de sensibilidade;
    
3. O receptor deve estar sintonizado na frequência correta;
    
4. O receptor deve estar sintonizado na frequência fundamental correta.
    

O limiar de sensibilidade atualmente implementado pode ser visto abaixo (valores em dBm):

![\begin{matrix} \scriptstyle{\rm SF7} & \scriptstyle{\rm SF8} & \scriptstyle{\rm SF9} & \scriptstyle{\rm SF10} & \scriptstyle{\rm SF11} & \scriptstyle{\rm SF12}\\ -124 & -127 & -130 & -133 & -135 & -137 \\ \end{matrix}](https://signetlabdei.github.io/lorawan/models/build/html/_images/math/32916788b8291d81c99b3aa76502bbabadf4490a.png)

Após a camada física (PHY) se conectar ao pacote recebido, ela agenda uma `EndReceive` chamada de função após a duração do pacote. A potência de recepção é considerada constante durante todo o processo de recepção do pacote. Quando a recepção termina, o método da instância da camada física é `EndReceive`chamado para determinar se o pacote foi perdido devido a interferência.`IsDestroyedByInterference``LoraInterferenceHelper`

A `IsDestroyedByInterference`função compara a potência de recepção do pacote desejado com a energia de interferência dos pacotes que se sobrepõem a ele, com base no fator de espalhamento (SF), e compara o valor de SIR obtido com a matriz de isolamento tabulada em [[goursaud2015dedicated]](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#goursaud2015dedicated) e reproduzida abaixo. Por exemplo, se o pacote desejado estiver usando SF7 e estiver (mesmo que parcialmente) sobreposto a dois pacotes usando SF10, a energia do sinal desejado (calculada como o produto da potência de recepção e da duração do sinal) é comparada à energia somada dos dois interferentes (calculada como o produto da potência do interferente no receptor e do tempo de sobreposição). A razão entre a energia desejada e a energia de interferência de cada fator de espalhamento (considerados separadamente) é então comparada à tabela abaixo, na qual as linhas identificam o SF do sinal desejado, enquanto as colunas representam o SF interferente que está sendo considerado. Se o SIR estiver acima do limite tabelado, o pacote é recebido corretamente e encaminhado para a camada MAC.

![\begin{matrix} & \scriptstyle{\rm SF7 } & \scriptstyle{\rm SF8 }& \scriptstyle{\rm SF9 }& \scriptstyle{\rm SF10} & \scriptstyle{\rm SF11} & \scriptstyle{\rm SF12}\\ \scriptstyle{\rm SF7 }& 6 &-16 &-18 &-19 &-19 &-20\\ \scriptstyle{\rm SF8 }& -24 &6 &-20 &-22 &-22 &-22\\ \scriptstyle{\rm SF9 }& -27 &-27 &6 &-23 &-25 &-25\\ \scriptstyle{\rm SF10} & -30 &-30 &-30 &6 &-26 &-28\\ \scriptstyle{\rm SF11} & -33 &-33 &-33 &-33 &6 &-29\\ \scriptstyle{\rm SF12} & -36 &-36 &-36 &-36 &-36 &6\\ \end{matrix}](https://signetlabdei.github.io/lorawan/models/build/html/_images/math/4e4fd11ad062170342cef13aa8f35f72e9b9362d.png)

Uma descrição completa do modelo de camada de ligação também pode ser encontrada em [[magrin2017performance]](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#magrin2017performance) e em [[magrin2017thesis]](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#magrin2017thesis) .

#### 18.2.1.2. Modelo de gateway [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#gateway-model "Link para este cabeçalho")

O chip instalado nos gateways LoRa requer atenção especial devido à sua arquitetura: como é caracterizado pela presença de 8 _caminhos de recepção_ paralelos , ele pode receber múltiplos pacotes em paralelo [[sx1301]](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#sx1301) . Esse comportamento é representado no simulador por meio de um `ReceptionPath`objeto que se comporta como um `EndDeviceLoraPhy`bloqueador de pacotes, conectando-se aos pacotes recebidos e comparando-os com outros para determinar a recepção correta usando a `LoraInterferenceHelper`instância do gateway. Um bloqueador de pacotes `GatewayLoraPhy`, então, é essencialmente um gerenciador dessa coleção de `ReceptionPath`objetos. Ao chegar um pacote, o gateway escolhe um caminho de recepção livre (se houver algum), marca-o como ocupado e o conecta ao pacote recebido. Assim que o `EndReceive`método agendado é executado, a instância do gateway `LoraInterferenceHelper` (que contém informações usadas por todos os bloqueadores `ReceptionPaths`de pacotes) é consultada e é decidido se o pacote foi recebido corretamente ou não.

Foram feitas algumas suposições adicionais sobre o comportamento de colaboração desses caminhos de recepção para estabelecer um modelo consistente, apesar da folha de dados do chip gateway SX1301 não detalhar completamente como o chip administra os caminhos de recepção disponíveis:

- Os caminhos de recebimento podem ser configurados para escutar pacotes de entrada em qualquer frequência;
    
- Os canais de recepção podem ser alocados livremente nas frequências disponíveis;
    
- Os caminhos de recebimento não precisam ser pré-configurados para escutar um determinado fator de espalhamento (portanto, o ponto 4 dos pré-requisitos mencionados acima para Dispositivos Finais não se aplica);
    
- Se um pacote estiver chegando e vários caminhos de recepção estiverem escutando o mesmo canal, apenas um deles se conectará ao pacote recebido;
    
- Se todos os caminhos de recepção em um canal estiverem bloqueados em um pacote de entrada e outro pacote chegar, o novo pacote será imediatamente marcado como perdido.
    

### 18.2.2. Modelo de camada MAC [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#mac-layer-model "Link para este cabeçalho")

Os modelos MAC contidos neste módulo visam implementar o padrão LoRaWAN. Para facilitar essa tarefa, uma série de classes auxiliares foram criadas para lidar com cabeçalhos, comandos MAC, canais lógicos e cálculos de ciclo de trabalho. Além disso, uma versão simplificada de um Servidor de Rede (NS) também é fornecida na forma de um aplicativo que pode ser instalado em um _ns-3_ `Node` e conectado aos gateways por meio de um `PointToPoint`link para simular um canal de backbone.

#### 18.2.2.1. Cabeçalhos, comandos MAC e sistema de endereçamento [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#headers-mac-commands-and-addressing-system "Link para este cabeçalho")

A estrutura de pacotes definida pelo padrão LoRaWAN é implementada por meio de duas classes que estendem a `Header`classe `LoRaWAN`: `LorawanMacHeader``LoRaWAN` e `LoRaWAN` `LoraFrameHeader`. Em particular, ` `LoraFrameHeader`LoRaWAN` pode incluir comandos MAC aproveitando as classes `LoRaWAN` `MacCommand`e ` `LoraDeviceAddress`LoRaWAN`, que são usadas para facilitar a serialização, desserialização e interpretação de comandos MAC e do sistema de endereçamento LoRaWAN.

Os comandos MAC são implementados estendendo a `MacCommand`classe. Cada classe filha é usada para definir um conjunto de variáveis ​​de comando, métodos para serializar e desserializar os comandos dentro de um objeto `LoraFrameHeader`e funções de retorno de chamada para a camada MAC para executar ações. Essa estrutura pode facilitar a implementação e o teste de comandos MAC personalizados, conforme permitido pela especificação.

A `LoraDeviceAddress`classe é usada para representar o endereço de um dispositivo LoRaWAN ED e para lidar com a serialização e desserialização.

#### 18.2.2.2. Canais lógicos e ciclo de trabalho [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#logical-channels-and-duty-cycle "Link para este cabeçalho")

Como o LoRaWAN opera em bandas não licenciadas sujeitas a restrições de ciclo de trabalho, uma série de objetos foi criada para monitorar o tempo de transmissão disponível e limitar a transmissão na camada MAC, caso as camadas superiores não estejam cientes dessas limitações. Um objeto `LoRaWAN` `LogicalLoraChannelHelper`é atribuído a cada `LorawanMac`instância e tem a função de monitorar todos os canais lógicos disponíveis (que podem ser adicionados e modificados com comandos MAC e são representados pela `LogicalLoraChannel`classe `LoRaWAN`) e de estar ciente da sub-banda em que se encontram (por meio de instâncias da `SubBand`classe `LoRaWAN`).

Além disso, para garantir o cumprimento das limitações do ciclo de trabalho, este objeto também registra todas as transmissões realizadas em cada canal e pode ser consultado pela `LorawanMac`instância para saber o próximo horário em que a transmissão será possível, de acordo com a regulamentação. Se uma transmissão de duração ![t_{\rm ar}](https://signetlabdei.github.io/lorawan/models/build/html/_images/math/a648c6f443fd90cf72197076a615956506aa19c8.png)for realizada pelo dispositivo em um canal cujo ciclo de trabalho, expresso em forma fracionária ![\rm dc](https://signetlabdei.github.io/lorawan/models/build/html/_images/math/ec31009297265e6724a791aa785acf3346731ecd.png), for , o tempo que o dispositivo precisa permanecer desligado é calculado de acordo com a seguinte fórmula:

![t_{\rm off} = \frac{t_{\rm air}}{\rm dc} - t_{\rm air}](https://signetlabdei.github.io/lorawan/models/build/html/_images/math/95ccaa7303a4220a0079a6e7275a68d66e1e6fe3.png)

Esse tempo é monitorado por sub-banda, de forma que, se dois canais estiverem sob a mesma regulamentação, uma transmissão em um deles também bloqueará o outro.

### 18.2.3. O Servidor de Rede [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#the-network-server "Link para este cabeçalho")

Este `NetworkServer`é um aplicativo que está sendo executado em um nó conectado aos gateways de simulação. Os gateways encaminham pacotes LoRa recebidos para o Servidor de Rede (NS) e esperam receber pacotes para transmitir no downlink para os Dispositivos de Encaminhamento (EDs) enviados pelo NS. Para manter o controle de todos os participantes da rede, o NS mantém duas listas de `DeviceStatus`objetos `GatewayStatus`, que representam o status atual de cada ED e gateway na rede, respectivamente. Esses objetos são usados ​​para controlar os pacotes de downlink que precisarão ser enviados durante as janelas de recepção dos EDs e também contêm ponteiros para as instâncias da camada MAC de cada gateway. Isso é feito para que seja possível consultar as limitações do ciclo de trabalho atual do gateway e sempre encaminhar pacotes de downlink para gateways que possam transmitir o pacote na rede LoRa. A versão atual do Servidor de Rede envia pacotes de downlink apenas para dispositivos que exigem um reconhecimento, ignorando o conteúdo do pacote e os comandos MAC que ele possa conter. A transmissão é realizada na primeira janela de recepção sempre que possível, e a segunda janela de recepção é usada somente quando não há mais recursos disponíveis para aproveitar a primeira oportunidade de resposta ao dispositivo. Comportamentos de NS mais complexos e realistas são certamente possíveis, porém também acarretam um custo de complexidade não desprezível.

## 18.3. Âmbito de aplicação e limitações [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#scope-and-limitations "Link para este cabeçalho")

Como esta ainda é uma primeira versão do módulo, algumas ressalvas são listadas abaixo.

### 18.3.1. Interferência entre protocolos [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#inter-protocol-interference "Link para este cabeçalho")

Como a `LoraChannel`classe só pode ser conectada às camadas PHY do LoRa, o modelo atualmente não consegue levar em conta a interferência de outras tecnologias.

Espera-se que, no futuro, seja possível lidar com a interferência entre protocolos aproveitando a `SpectrumChannel`classe, assim que modelos mais precisos de como a interferência afeta os sinais LoRa estiverem disponíveis.

### 18.3.2. Interferência entre canais [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#inter-channel-interference "Link para este cabeçalho")

A interferência entre canais parcialmente sobrepostos não é verificada. Além disso, atualmente não existe um modelo que contabilize a interferência entre sinais que utilizam larguras de banda diferentes.

### 18.3.3. Servidor de Rede [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#network-server "Link para este cabeçalho")

A implementação atual do Servidor de Rede tenta fornecer uma estrutura geral para lidar com Dispositivos de Engate (EDs) e Gateways (GWs) em uma rede, mas ainda carece de código possivelmente complexo para simular recursos avançados, como diferentes algoritmos de Taxa de Dados Adaptativa (ADR), resposta aos comandos MAC do ED e suporte a procedimentos de junção. Outras limitações do Servidor de Rede são a ausência de um protocolo para comunicação com os Gateways (já que não existem protocolos oficiais) e o fato de informar o gateway em tempo real sobre as mensagens de downlink que ele precisa enviar (em outras palavras, não há "reserva" prévia do recurso do gateway, e os pacotes de downlink têm prioridade sobre os pacotes de entrada no gateway).

Até o momento, a implementação do Servidor de Rede deve ser considerada um recurso experimental, sujeito a bugs ainda não descobertos.

### 18.3.4. Classes de Dispositivos [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#device-classes "Link para este cabeçalho")

Atualmente, apenas dispositivos finais da Classe A são suportados.

### 18.3.5. Parâmetros regionais [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#regional-parameters "Link para este cabeçalho")

Como os parâmetros do LoRaWAN, como a configuração padrão de canais e a interpretação dos comandos MAC, variam de acordo com a região operacional da rede, `LorawanMacHelper`este documento inclui métodos para especificar a região. Embora a implementação atual esteja preparada para suportar diferentes configurações de rede com base na região em que se destina a operar, atualmente apenas a região da UE, utilizando a sub-banda de 868 MHz, é suportada.

### 18.3.6. Detalhes da camada MAC [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#mac-layer-details "Link para este cabeçalho")

Alguns detalhes que não são cruciais para a avaliação do desempenho do sistema de uma rede ainda precisam ser implementados. Estes incluem:

- Contadores de quadros, tanto nos dispositivos finais quanto no DeviceStatus do servidor de rede.
    
- Configuração adequada dos indicadores ADR (nenhum mecanismo ADR foi implementado ainda)
    
- Gerenciamento conjunto de procedimentos (tanto no NS quanto nos EDs)
    

## 18.4. Utilização [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#usage "Link para este cabeçalho")

Uma utilização típica do modelo segue alguns paradigmas típicos _do ns-3_ , como o uso de auxiliares para configurar uma rede complexa. Esta seção ilustra a configuração de uma rede LoRaWAN usando o módulo e algumas outras classes auxiliares que não foram descritas nas seções anteriores porque são usadas principalmente para configurar a rede.

### 18.4.1. Auxiliares [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#helpers "Link para este cabeçalho")

O `lorawan`módulo inclui funções auxiliares para configurar as camadas PHY e MAC em um grande número de dispositivos. As duas camadas são divididas em duas classes diferentes, `PHY` `LorawanMacHelper`e `LoraPhyHelper``MAC`, que podem ser utilizadas por um `LoraHelper`objeto `LoRa` para configurar completamente um dispositivo LoRa (tanto para EDs quanto para GWs). Como as funções auxiliares são de propósito geral (ou seja, podem ser usadas tanto para configuração de EDs quanto de GWs), é necessário especificar o tipo de dispositivo por meio do `SetDeviceType`método `configure` antes que o `Install`método `configure` possa ser chamado.

O código `LorawanMacHelper`também expõe um método para configurar automaticamente os fatores de espalhamento (Spreading Factors) usados ​​pelos dispositivos participantes da rede, com base nas condições do canal e no posicionamento dos dispositivos e gateways. Esse procedimento está contido no método estático `SetSpreadingFactorsUp`e funciona tentando minimizar o tempo de transmissão dos pacotes, atribuindo assim o menor fator de espalhamento possível que permita a recepção por pelo menos um gateway. Deve-se notar que essa é uma heurística e que não garante que a distribuição do fator de espalhamento seja ótima para o melhor funcionamento da rede. De fato, encontrar tal distribuição com base no cenário da rede ainda é um desafio em aberto.

### 18.4.2. Atributos [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#attributes "Link para este cabeçalho")

Atualmente, os seguintes atributos estão disponíveis:

- `Interval`e `PacketSize`determinar `PeriodicSender`o intervalo entre os envios de pacotes do aplicativo, bem como o tamanho dos pacotes gerados pelo aplicativo.
    

### 18.4.3. Rastrear fontes [](https://signetlabdei.github.io/lorawan/models/build/html/lorawan.html#trace-sources "Link para este cabeçalho")

Diversas fontes de rastreamento podem ser usadas para monitorar eventos ao longo da simulação, principalmente em relação ao tempo de vida de um pacote. Na camada física (PHY), as seguintes fontes de rastreamento estão disponíveis:

- Em `LoraPhy`(ambos `EndDeviceLoraPhy`e `GatewayLoraPhy`):
    
    - `StartSending`, disparado quando uma camada física (PHY) começa a transmitir um pacote;
        
    - `PhyRxBegin`, disparado quando uma camada física (PHY) fica bloqueada em um pacote;
        
    - `PhyRxEnd`, disparado quando a recepção de um pacote pela camada física (PHY) termina;
        
    - `ReceivedPacket`, disparado quando um pacote é recebido corretamente;
        
    - `LostPacketBecauseInterference`, disparado quando um pacote é perdido devido à interferência de outras transmissões;
        
    - `LostPacketBecauseUnderSensitivity`, disparado quando uma camada física (PHY) não consegue se fixar em um pacote porque ele está sendo recebido com uma potência abaixo da sensibilidade do dispositivo;
        
- Em `EndDeviceLoraPhy`:
    
    - `LoraPacketBecauseWrongFrequency`É disparado quando um pacote recebido utiliza uma frequência diferente daquela em que a camada física (PHY) está escutando;
        
    - `LoraPacketBecauseWrongSpreadingFactor`é disparado quando um pacote de entrada está usando um SF diferente daquele para o qual a camada física (PHY) está escutando;
        
    - `EndDeviceState`É utilizado para monitorar o estado da camada física (PHY) do dispositivo.
        
- Em `GatewayLoraPhy`:
    
    - `LostPacketBecauseNoMoreReceivers`é disparado quando um pacote é perdido porque não há mais caminhos de recepção disponíveis para se conectar ao pacote de entrada;
        
    - `OccupiedReceptionPaths`É utilizado para controlar o número de caminhos de recepção ocupados dentre os 8 disponíveis no portal;
        
- Em `LorawanMac`(ambos `EndDeviceLorawanMac`e `GatewayLorawanMac`):
    
    - `CannotSendBecauseDutyCycle`É utilizado para controlar o número de vezes que um pacote proveniente da camada de aplicação não pode ser enviado por nenhum dos canais disponíveis devido a limitações do ciclo de trabalho;
        
- Em `EndDeviceLorawanMac`:
    
    - `DataRate`Monitora a taxa de dados utilizada pelo dispositivo;
        
    - `LastKnownLinkMargin`Mantém o controle da última margem de enlace das transmissões de uplink deste dispositivo; essa informação é coletada por meio dos `LinkCheck` comandos MAC;
        
    - `LastKnownGatewayCount`Mantém o controle do último número conhecido de gateways que este dispositivo consegue al