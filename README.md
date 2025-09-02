<img width="800" height="250" alt="Logs_Analytics" src="https://github.com/user-attachments/assets/7fe5ee5e-9555-490f-b2be-8a67854fb7a2" />

Uma aplicação **full-stack** de análise de logs que permite aos usuários registrar logs, monitorar métricas, acompanhar alertas e filtrar logs por serviço ou nível de gravidade.  

---

## Demonstração


https://github.com/user-attachments/assets/a63fb80e-1d6e-4f4d-b221-104022b5e646




## Funcionalidades

- **Gerenciamento de Logs**: Criar, rastrear e armazenar logs por serviço e nível.  
- **Métricas e Agregação**: Visualizar métricas agregadas por serviço ou nível em um intervalo de tempo.  
- **Alertas**: Geração automática de alertas quando a contagem de logs ultrapassa o limite configurável.  
- **Filtragem e Pesquisa**: Filtrar logs por serviço, nível e período de tempo.  
- **Monitoramento de Tarefas**: Acompanhar o status de tarefas do Celery para processamento assíncrono.  
- **Interface Interativa**: Dashboard em React com gráficos, tabelas e busca.  
- **Suporte a CORS**: Permite integração com clientes externos.


## Tecnologias

- **Backend**: FastAPI, Celery   
- **Banco de Dados**: PostgreSQL (via SQLAlchemy async)  
- **Frontend**: React + TypeScript
- 

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

## Setup (Desenvolvimento local)

### 1 - Clone the Repository
```bash
git clone https://github.com/orafaelmatos/logs-analytics.git
cd logs-analytics
```
### 2 - Run with Docker (recommended)
```bash
docker-compose up --build
```

### A aplicação vai esta disponível
 -  [http://localhost:8080](http://localhost:8080)

