# Meta Marketing API Connector

Conector OpenAPI para a Meta Marketing API v22.0, fornecendo acesso a métricas de campanhas e gestão de anúncios.

## Estrutura

O projeto está organizado em três especificações OpenAPI principais:

1. `maind.yaml`: Configuração principal do conector
   - Configurações gerais da API
   - Esquemas de segurança
   - Headers comuns
   - Respostas de erro padrão
   - Rate limiting e performance

2. `campaign-insights.yaml`: Endpoints de análise
   - Métricas de campanha
   - Breakdowns
   - Schemas específicos de insights
   - Referências ao arquivo principal

3. `campaign-management.yaml`: Endpoints de gestão
   - Tokens de acesso
   - CRUD de campanhas
   - Schemas específicos de campanhas
   - Referências ao arquivo principal

## Rate Limits

- **Standard Tier**:
  - 9000 pontos por 300s
  - 1 ponto por leitura
  - 3 pontos por escrita
  - Bloqueio de 60s quando excedido

- **Development Tier**:
  - 60 pontos por 300s
  - Mesmo sistema de pontos
  - Bloqueio de 300s quando excedido

## Performance

- Cache: 5 minutos (300s)
- Timeout: 30s (sync), 1h (async)
- Compressão: habilitada
- Batch size: 100 itens

## Métricas Validadas

### Base (Sempre Disponíveis)
- impressions
- reach
- spend
- inline_post_engagement

### Estendidas (Quando Disponíveis)
- video_p25_watched_actions
- video_p50_watched_actions
- video_p75_watched_actions
- video_p95_watched_actions
- video_avg_time_watched_actions

## Breakdowns

Suporte a um breakdown por vez:
- publisher_platform
- platform_position
- age
- gender
- region

## Períodos

- Curto: today, yesterday, last_3d, last_7d
- Médio: last_30d
- Longo: this_month, last_month

## Versão

Atual: 1.4.0

## Licença

MIT
