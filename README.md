# Análise de Inventário e Operação — Fulfillment Center de Marketplace

Projeto de portfólio simulando o trabalho de um **analista de dados de inventário** em uma rede de Fulfillment Centers de marketplace, no modelo em que o seller envia o estoque e a plataforma armazena, separa e expede (como o Mercado Livre Full).

A partir de extrações brutas de WMS, o notebook trata os dados, valida a base e calcula em **DuckDB (SQL)** as métricas de eficiência do inventário e da operação diária. Cada métrica vem com a fórmula e a leitura de negócio.

> Dados **100% sintéticos**, criados para estudo. Não representam números reais de nenhuma empresa.

**Escopo:** 3 FCs (SP, MG, BA) · 620 sellers · 4.200 SKUs · ~264 mil pedidos · jul a out/2026

## Métricas e fórmulas

### Eficiência do inventário
| Métrica | Fórmula |
|---|---|
| IRA por endereço | endereços contados sem divergência ÷ endereços contados |
| Acuracidade em unidades | 1 − Σ\|q_final − q_sistema\| ÷ Σ q_sistema |
| Acuracidade em valor | 1 − Σ\|Δq\|·preço ÷ Σ q_sistema·preço |
| Taxa de erro de contagem | divergências da 1ª contagem desmentidas na recontagem ÷ divergências na 1ª contagem |
| Shrinkage % | \|Σ ajustes·preço\| ÷ valor expedido |
| Aging | data de referência − data de entrada do lote (faixas 0-30, 31-60, 61-90, 91-180, 180+) |
| Cobertura (DOH) | estoque atual ÷ venda média diária (30 dias) |
| Giro anualizado (aprox.) | expedido 30 dias × 12 ÷ estoque atual |
| Sell-through 30d | expedido 30d ÷ (expedido 30d + estoque atual) |
| Ocupação | endereços ocupados ÷ capacidade de endereços |
| Cancelamento por falta | pedidos cancelados por falta de estoque ÷ pedidos recebidos |

### Operação diária
| Métrica | Fórmula |
|---|---|
| Dock-to-stock | fim da armazenagem − chegada do veículo (P50 / P90) |
| Pontualidade de agendamento | ASNs que chegaram até agendamento + 30 min ÷ ASNs |
| Divergência de ASN | Σ\|recebido − declarado\| ÷ Σ declarado |
| Avaria no recebimento | unidades avariadas ÷ unidades recebidas |
| On-time shipping (OTS) | pedidos expedidos até o limite ÷ pedidos expedidos |
| Order cycle time | expedição − pedido (P50 / P90) |
| Backlog | pedidos recebidos e não expedidos às 22h |
| UPH | unidades processadas ÷ horas trabalhadas |
| Aderência à meta | UPH real ÷ UPH meta |
| Acuracidade de picking | 1 − pedidos com erro de separação ÷ pedidos expedidos |
| DPMO | ocorrências ÷ pedidos expedidos × 1.000.000 |
| Pedido perfeito | pedidos no prazo e sem ocorrência ÷ pedidos válidos |

## Principais resultados
- Validação cruzada pedidos × apontamentos: **23,7% → 100%** dos turnos conciliados após o tratamento
- Nenhum FC atinge 98% de IRA; itens pequenos e caros ficam em ~93%
- O cancelamento por falta acompanha a acuracidade: **1,32%** no FC de pior IRA, contra 0,38% no melhor
- R$ 487 mil em perdas em 4 meses, lideradas por avaria interna
- FC SP com **91% de ocupação** e lotes com mais de 90 dias ocupando posição
- FC MG perdeu o prazo na campanha 10/10 (OTS de 93,2% no período)
- Scorecard diário por FC com status contra a meta, gerado para qualquer data

## Estrutura
```
├── data/raw/                                   # extrações do WMS
├── notebooks/analise_inventario_fulfillment.ipynb
└── requirements.txt
```

## Dados
| Arquivo | Conteúdo |
|---|---|
| `fcs.csv` | FCs e capacidade de endereços |
| `sellers.csv` | Sellers com reputação |
| `skus.csv` | Anúncios/SKUs (inventory_id), categoria, tamanho, preço |
| `pedidos.csv.gz` | Pedidos com horários de pedido, limite, picking, packing, expedição e status |
| `ocorrencias_qualidade.csv` | Reclamações pós-expedição (item errado, faltante, avaria) |
| `recebimentos.csv` | ASNs com agendamento, chegada, conferência, armazenagem e divergências |
| `apontamentos_produtividade.csv` | Horas e unidades por FC, dia, turno e processo |
| `contagens_ciclicas.csv` | Contagens com saldo do sistema, 1ª contagem e recontagem |
| `ajustes_inventario.csv` | Ajustes de saldo com motivo |
| `posicao_estoque.csv` | Foto do estoque por endereço e lote em 31/10/2026 |

## Como executar
```bash
pip install -r requirements.txt
jupyter notebook notebooks/analise_inventario_fulfillment.ipynb
```

## Stack
Python · DuckDB · pandas · matplotlib · Jupyter
