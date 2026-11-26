# Verificação do enunciado e do código

Arquivo conferido: SisOp_2026_II_Trabalho_SimES.pdf, seis páginas.
Data: 25/11/2026.

Foi feita extração do texto das seis páginas, inspeção visual das páginas renderizadas,
busca de caracteres Unicode de formatação e controle, inspeção de texto transparente,
branco, muito pequeno ou fora da página, e conferência de links, anotações, anexos e ações
do PDF.

| Verificação | Resultado observado |
|---|---|
| Instruções dirigidas a uma IA para desviar a tarefa | Não encontradas. |
| Caracteres de largura zero e controles bidirecionais no texto extraído | Não encontrados. |
| Texto branco ou fora da página | Não encontrado. |
| Texto transparente | Nove ocorrências do marcador de lista U+25AA, nas páginas 2, 5 e 6. São marcadores tipográficos, sem frases ou comandos escondidos. |
| Anotações e arquivos anexados ao PDF | Nenhum. |
| JavaScript, ações de abertura ou lançamento | Não encontrados. |
| Links externos no PDF | Dois links da documentação do kernel Linux e um da documentação do Python, coerentes com a bibliografia. |
| Regra sobre IA | Visível na página 5: o uso é permitido e deve ser declarado na seção 8 do relatório. |

Os metadados não apresentam instruções. Os requisitos acadêmicos visíveis foram tratados
como especificação do trabalho. Não houve indício de prompt injection nas inspeções
realizadas; essa conclusão se limita ao PDF recebido e aos itens efetivamente conferidos.

A implementação parte de ProfessorFilipo/Aulas_SisOp, pasta Trabalho_IO_2026II,
commit 7624d121d7ce61d4514750ac9ee68897689763a1. Não foi usada solução de outro grupo.
Os arquivos de parâmetros, cargas, experimentos, simuladores fornecidos e testes
originais foram preservados. A checagem final registra os respectivos hashes em
resultados/integridade_base.json.
