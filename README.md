# Plataforma de Análise de Logs
Uma aplicação **full-stack** de análise de logs que permite aos usuários registrar logs, monitorar métricas, acompanhar alertas e filtrar logs por serviço ou nível de gravidade.  
O backend é construído com **FastAPI** e **Celery** para processamento assíncrono, enquanto o frontend é feito com **React + TypeScript** para uma interface moderna e interativa.

---


## Funcionalidades

- **Gerenciamento de Logs**: Criar, rastrear e armazenar logs por serviço e nível.  
- **Métricas e Agregação**: Visualizar métricas agregadas por serviço ou nível em um intervalo de tempo.  
- **Alertas**: Geração automática de alertas quando a contagem de logs ultrapassa o limite configurável.  
- **Filtragem e Pesquisa**: Filtrar logs por serviço, nível e período de tempo.  
- **Monitoramento de Tarefas**: Acompanhar o status de tarefas do Celery para processamento assíncrono.  
- **Interface Interativa**: Dashboard em React com gráficos, tabelas e busca.  
- **Suporte a CORS**: Permite integração com clientes externos.


## Backend

- **Framework**: FastAPI  
- **Tarefas Assíncronas**: Celery  
- **Banco de Dados**: PostgreSQL (via SQLAlchemy async)  
- **Modelos Principais**: `LogMetric`, `LogCreate`  
- **Limite de Alerta**: Configurável via `ALERT_THRESHOLD`

### Endpoints da API

#### Logs
- `POST /logs/` – Criar novo log.  
- `GET /logs/recent` – Logs recentes (padrão 100).  
- `GET /logs/service/{service_name}` – Logs filtrados por serviço.  
- `GET /logs/level/{level_name}` – Logs filtrados por nível.

#### Métricas
- `GET /metrics/service/{service_name}` – Métricas agregadas por serviço.  
- `GET /metrics/level/{level_name}` – Métricas agregadas por nível.

#### Alertas
- `GET /alerts/` – Logs que ultrapassam o limite de alerta, com filtros opcionais por serviço, nível ou período.

#### Tarefas
- `GET /tasks/{task_id}` – Verificar status de uma tarefa Celery.

---


## Frontend

- **Framework**: React + TypeScript  
- **Funcionalidades**:
  - Dashboard com visualização de métricas.
  - Lista de logs com filtros.
  - Visão geral de alertas.
  - Integração com a API do backend.

---
