# Hipóteses registradas antes dos experimentos

Registro: 25/11/2026. Este arquivo foi criado antes da primeira execução dos experimentos.
As hipóteses não foram ajustadas aos resultados. Os vereditos e as explicações posteriores
ficam em RELATORIO.md. Fonte conceitual: Silberschatz, Galvin e Gagne, 9ª edição.

| Experimento | Hipótese prévia | Base conceitual |
|---|---|---|
| X1 | SSTF e SCAN devem reduzir deslocamento e resposta em cargas aleatórias ou concentradas sob fila. Na carga sequencial, a vantagem deve diminuir; SSTF pode aumentar a maior espera. | Seção 10.4: ordenação espacial e justiça. |
| X2 | No HDD, interrupção deve usar muito menos CPU que polling. No dispositivo rápido, a diferença diminui e o custo fixo por bloco pode tornar interrupção mais cara que espera ocupada durante o atendimento. | Seções 13.2.1 e 13.2.2. |
| X3 | A leitura sequencial deve aproveitar transferência de blocos vizinhos; acessos diretos devem pagar mais rotação. As médias das duas cargas também dependem dos tamanhos e das operações, portanto não isolam apenas o método de acesso. | Capítulo 11, métodos de acesso; modelo de busca e rotação. |
| X4 | Cada diretório adicional deve acrescentar exatamente uma leitura por open, sem cache de diretórios. O tempo deve crescer, mas não necessariamente de forma perfeitamente linear. | Capítulo 11, diretórios hierárquicos; regras de resolver. |
| X5 | A soma das tabelas dos processos deve superar a tabela global quando vários processos abrem os mesmos arquivos. As posições dos handles permanecem independentes e o contador global soma as aberturas. | Capítulo 11, tabelas de arquivos abertos. |
| X6 | Aumentar a capacidade deve melhorar a taxa de acerto nesta carga com reuso. LRU deve tender a superar FIFO. Write-back deve reduzir escritas físicas, mantendo blocos sujos que podem ser perdidos na queda; write-through não mantém blocos sujos. | Seções 13.4.3 e 12.6. |
| X7 | Sob maior taxa de chegada, a espera tende a aumentar. DEADLINE deve limitar o adiamento de requisições antigas em comparação com SSTF quando existirem prazos vencidos; isso pode aumentar a resposta média ou o deslocamento. | Seção 10.4; compromisso entre localidade e justiça. |
| X11 | A contígua deve ter acesso barato, mas pode falhar por fragmentação externa e realocar ao crescer. A encadeada deve pagar leituras de ponteiros no acesso direto. FAT elimina esse custo de disco ao manter a tabela em memória. A indexada troca blocos e leituras de índice por acesso limitado a um ou dois níveis. | Seções 12.4 e 12.5. |
| X12 | A cache deve absorver metadados repetidos e reduzir a resposta. A indexada deve gerar mais requisições sem cache. O efeito do escalonador depende da fila que a carga realmente produz. | Seções 10.4, 12.4 e 13.4.3; composição das camadas. |
| X13 | Flash deve responder mais rapidamente nas cargas aleatórias, por não pagar busca e rotação. A amplificação de escrita só deve ultrapassar 1 quando houver coleta de lixo com cópia de páginas válidas; as cargas oficiais podem não preencher o dispositivo. | Capítulo 10 e regras de páginas, apagamento e FTL do enunciado. |

Experimento suplementar planejado: usar flash de capacidade pequena, preencher a área
lógica e sobrescrever páginas com semente fixa, para provocar coleta de lixo. Seus resultados
serão separados dos CSVs oficiais e não substituirão X13.
