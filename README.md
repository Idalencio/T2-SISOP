# SimES - T2 de Sistemas Operacionais

**Pedro Rocha Idalencio** · PUCRS · 2026/II · Prof. Filipo Novo Mór

Simulador de entrada e saída e de sistema de arquivos, desenvolvido a partir do código-base da disciplina.

- [Relatório em PDF](Relatorio_SimES_Pedro_Idalencio.pdf)
- [Relatório em Markdown](RELATORIO.md)
- [Hipóteses registradas antes dos experimentos](HIPOTESES.md)
- [Guia para a arguição](GUIA_PARA_ARGUICAO.md)
- [Conferência do enunciado](AUDITORIA_ENUNCIADO.md)

## Escopo

Núcleo completo, cache LRU/FIFO (M1), escalonadores avançados (M2), alocação encadeada/FAT/indexada (M6), integração entre camadas e bônus de armazenamento flash. M3, M4 e M5 ficaram fora do escopo.

São 35 testes aprovados e quatro pulados, todos de módulos não escolhidos. Os dez experimentos do escopo totalizam 118 execuções oficiais. Os CSVs foram reproduzidos byte a byte em uma segunda execução.

## Executar

Python 3.8 ou superior. O simulador e os testes usam apenas a biblioteca padrão. No Windows, use `py` em lugar de `python3`.

```text
python3 executar.py testes
python3 executar.py experimentos
python3 graficos.py
python3 experimentos_extras.py
python3 graficos_complementares.py
python3 ferramentas/validar_entrega.py
```

Os dois scripts de gráficos precisam de matplotlib. Os demais comandos acima não precisam dessa dependência. Os parâmetros, cargas e experimentos oficiais foram mantidos.

O suplemento de flash usa outra capacidade, com semente fixa e reserva efetiva declaradas; seus dados ficam separados dos oficiais em `resultados/extra_flash_gc.csv`.

## Evidências

- `resultados/`: indicadores oficiais, suplemento, testes e registros de conferência.
- `graficos/`: gráficos oficiais e figuras complementares do relatório.
- `grupo.json`: integrante, módulos e endereço do repositório.
- `Historico_SimES.bundle`: histórico Git local, incluindo o registro das hipóteses anterior à implementação e à execução dos experimentos. Os hashes locais citados no relatório pertencem a esse histórico.

Para repetir a conferência de integridade e de reprodução dos CSVs:

```text
python3 ferramentas/conferir_reproducibilidade.py
```

## Entrega

No Moodle, enviar somente o PDF do relatório até 26/11/2026, às 23h59. Código, resultados e gráficos ficam neste repositório público, citado no PDF. O guia de arguição é material de apoio.

A declaração de autoria e uso de IA está na seção 8 do relatório.

## Código-base

ProfessorFilipo/Aulas_SisOp, pasta Trabalho_IO_2026II, commit `7624d121d7ce61d4514750ac9ee68897689763a1`:

https://github.com/ProfessorFilipo/Aulas_SisOp/tree/main/Trabalho_IO_2026II
