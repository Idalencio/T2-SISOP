# SimES - entrega de Pedro Rocha Idalencio

O núcleo, M1, M2, M6, a integração e o bônus flash estão implementados. As hipóteses foram registradas antes dos experimentos. Foram executadas 118 configurações oficiais; os resultados foram reproduzidos byte a byte numa execução independente.

## Arquivos principais

- `RELATORIO.md`: relatório no modelo obrigatório, com hipóteses, tabelas, figuras, análise, limitações, fontes e declaração de IA.
- `Relatorio_SimES_Pedro_Idalencio.pdf`: versão do relatório para enviar no Moodle.
- `GUIA_PARA_ARGUICAO.md`: perguntas, respostas e treinos para explicar o código.
- `AUDITORIA_ENUNCIADO.md`: verificação de instruções escondidas e caracteres invisíveis.
- `HIPOTESES.md`: registro prévio.
- `resultados/` e `graficos/`: evidências usadas no relatório.

Repositório do trabalho: `https://github.com/Idalencio/T2-SISOP`. O validador confere os arquivos locais; a acessibilidade pública também deve ser conferida pelo link do repositório.

## Conferência local

```text
python3 executar.py testes
python3 ferramentas/validar_entrega.py
```

São 35 testes aprovados e quatro pulados, referentes a M3, M4 e M5, fora do escopo. O escopo realizado supera o mínimo de uma entrega individual.

## Reproduzir resultados e gráficos

```text
python3 executar.py experimentos
python3 graficos.py
python3 experimentos_extras.py
python3 graficos_complementares.py
python3 ferramentas/conferir_reproducibilidade.py
```

No Windows, use `py` em lugar de `python3`. Só os gráficos precisam de matplotlib. Não altere parâmetros, cargas ou experimentos oficiais. O suplemento de flash é separado, com capacidade e semente declaradas.

## Entrega no Moodle

Prazo: 26/11/2026, às 23h59. Envie somente o PDF. Antes, confirme que o repositório é público e abre sem login. Código, CSVs e gráficos precisam estar publicados antes do prazo. O professor pode pedir explicação ou alteração do código durante a arguição.
