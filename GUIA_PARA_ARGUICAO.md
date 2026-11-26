# Guia para explicar o SimES

Pedro Rocha Idalencio · Sistemas Operacionais · 2026/II

Este guia acompanha o relatório. Antes da apresentação, execute os comandos e acompanhe as funções indicadas. O professor pode pedir uma mudança no código, não apenas uma definição.

## O que foi feito

| Parte | Ideia principal | Arquivo para abrir |
|---|---|---|
| Sistema de arquivos | Transforma caminhos e operações em acessos a blocos. | simes/arquivos/sistema.py |
| Alocação | Define onde os blocos de cada arquivo ficam. | simes/arquivos/alocacao.py |
| Cache | Evita repetir acesso ao disco quando o bloco está na memória. | simes/es/cache.py |
| Escalonador | Escolhe qual pedido pendente o disco atende agora. | simes/es/escalonadores.py |
| Dispositivo | Calcula quanto custa atender o pedido. | simes/disco.py |
| Integração | Converte o histórico de arquivos para a fila de E/S. | simes/integracao.py |

## Perguntas prováveis

**Qual a diferença entre SSTF e SCAN?** SSTF escolhe o pedido mais próximo da cabeça. SCAN segue uma direção e só volta depois de ir à borda quando acaba o trabalho à frente. SSTF pode adiar um pedido distante; SCAN pode gastar movimento indo à borda.

**SCAN e LOOK são iguais?** A diferença é a borda. LOOK inverte no último pedido; SCAN vai ao limite do disco. Na fila do livro, subindo a partir de 53, LOOK percorre 299 cilindros e SCAN, 331.

**O retorno do C-SCAN conta?** Sim. Ele vai até o maior cilindro, retorna a zero e continua subindo. Não atende os pedidos durante esse retorno, mas o deslocamento entra na conta.

**O que o DEADLINE faz?** Se algum pedido venceu o prazo, atende o menor prazo vencido. Sem vencidos, funciona como SSTF. O prazo de leitura é 200 ms e o de escrita é 2.000 ms. Isso dá prioridade, mas não garante terminar em 200 ms.

**Por que a carga sequencial foi tão ruim com FCFS?** São dois processos lendo/escrevendo sequencialmente em regiões distantes. Ao alternar os processos, FCFS atravessa o disco repetidamente. A sequência de cada processo é boa, mas a sequência global da fila não é.

**Polling sempre gasta mais CPU?** Não neste modelo. Polling custa o tempo do serviço. Interrupção custa 0,017 ms por bloco. No dispositivo rápido, oito blocos levam 0,064 ms, menos que os 0,136 ms de CPU cobrados para interrupções. O modelo não faz a CPU atrasar o dispositivo, então isso não é uma recomendação geral de driver.

**Qual a diferença entre LRU e FIFO?** LRU expulsa o bloco que está há mais tempo sem uso. FIFO expulsa o que entrou primeiro. Ler um bloco muda sua posição na LRU; na FIFO, não muda.

**Write-through ou write-back?** Write-through encaminha toda escrita ao disco. Write-back mantém o bloco sujo na memória e pode juntar várias mudanças antes de gravar. Ele reduz escritas, mas mantém dados pendentes. Em X6, os lotes do sync também podem aumentar a latência.

**Por que não dizer que write-through perde zero dados em qualquer queda?** O CSV conta apenas blocos sujos residentes. Não conta toda a fila de escritas nem simula uma recuperação. Zero nessa coluna é uma propriedade da medição didática, não uma garantia geral de hardware.

**Para que servem duas tabelas de arquivos abertos?** A do processo guarda handle, modo e posição. A global guarda o arquivo e o total de aberturas. Dois handles podem apontar para o mesmo arquivo e ter posições diferentes. Em X5, foram até 24 handles para doze arquivos.

**O que acontece ao excluir um arquivo aberto?** O nome some do diretório, mas os handles ainda conseguem usá-lo. Os blocos só são liberados quando o número de links é zero e a última abertura é fechada. Veja `unlink`, `close` e o teste com três handles.

**Como contar o custo de /a/b/f?** Para resolver, lê raiz, /a e /a/b: três leituras. `open` só resolve e atualiza tabelas. `create` ainda grava o diretório pai; `mkdir` grava o pai e o diretório novo.

**Por que 2.052 blocos livres não evitaram ENOSPC?** A contígua precisa de um único trecho grande. Em X11, os blocos livres ficaram espalhados em cinquenta trechos, sendo o maior de 154 blocos. Falta espaço contíguo para algumas extensões.

**Como encadeada, FAT e indexada diferem?** Na encadeada, é preciso seguir os ponteiros dos blocos. Na FAT, os ponteiros ficam em memória e não custam leitura de disco no exercício. Na indexada, são lidos um ou dois blocos de índice. A FAT parece ótima aqui porque o modelo não cobra RAM ou CPU da tabela.

**Por que mais acessos não significaram mais tempo em X11?** Acessos consecutivos podem evitar rotação. Alternar índice e dados pode exigir mais reposicionamento e rotação. Importa onde e em que ordem se acessa, além da quantidade de blocos.

**Por que a indexada com cache parece tão rápida em X12?** Ela gera muitos pedidos extras de índices, que são repetidos e baratos quando entram na cache. Isso aumenta o denominador da média por requisição. A média menor não prova que a operação inteira de arquivo ficou mais rápida.

**Como funciona o flash?** O endereço lógico aponta para uma página física. Ao sobrescrever, grava numa página apagada nova e invalida a antiga. A coleta copia páginas ainda válidas de um bloco e só então apaga o bloco inteiro.

**O que é amplificação de escrita?** É o total de páginas programadas dividido pelas páginas pedidas pelo host. No extra aleatório: 129.916 / 20.480 = 6,3436. A diferença de 109.436 páginas são cópias da coleta.

**Por que o oficial teve amplificação 1 e o extra 6,34?** O oficial grava muito menos que a capacidade física, então não precisa de coleta. O extra preenche um dispositivo menor e faz sobrescritas. Ele foi separado dos resultados oficiais e declara sua capacidade e semente.

## Treinos rápidos no código

1. Em `SSTF.escolher`, encontre a expressão que calcula a distância e explique por que o primeiro índice vence um empate.
2. Em `SCAN.escolher`, aponte onde a borda entra em `passar_por`. Compare com LOOK.
3. Em `Cache._tocar`, confira por que só LRU muda a ordem. Faça a sequência: inserir 1, inserir 2, ler 1, inserir 3. Qual sai em cada política?
4. Em `close`, acompanhe o contador global até zero e encontre a condição que libera um arquivo sem links.
5. Em `AlocadorIndexado`, calcule os índices necessários para 10, 1.024, 1.025 e 2.000 blocos: respectivamente 1, 1, 3 e 3.
6. Em `DiscoFlash._coletar`, encontre as cópias das páginas válidas e o acréscimo do custo de apagamento.

## Comandos para conferir

No Windows, troque `python3` por `py`.

```text
python3 executar.py testes
python3 executar.py es --carga cargas/es_aleatoria.txt --escalonador SSTF
python3 executar.py arquivos --carga cargas/fs_compilador.txt
python3 executar.py experimentos
python3 graficos.py
python3 experimentos_extras.py
python3 graficos_complementares.py
python3 ferramentas/validar_entrega.py
```

Os resultados oficiais são sobrescritos pelo comando de experimentos. `graficos.py` e o script de gráficos complementares precisam de matplotlib; o simulador e os testes usam somente a biblioteca padrão.

## Antes de enviar

O prazo informado é 26/11/2026, às 23h59. Envie apenas o PDF do relatório no Moodle. O repositório citado precisa estar público, com código, resultados e gráficos, e abrir sem autenticação. A declaração de IA deve corresponder à assistência recebida. Revise o relatório e pratique as explicações antes da arguição.
