# 🚨 Prometheus + Alertmanager + Grafana Monitoring

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-API-black?logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Container-2496ED?logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker%20Compose-Multi--Container-2496ED?logo=docker&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C?logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-Dashboard-F46800?logo=grafana&logoColor=white)
![Alertmanager](https://img.shields.io/badge/Alertmanager-Alerting-E6522C?logo=prometheus&logoColor=white)

## 📌 Description

Projet de monitoring et de gestion des alertes avec **Flask, Prometheus, Alertmanager et Grafana**.

L'application Flask expose des métriques que Prometheus collecte régulièrement. Des règles permettent de détecter une indisponibilité de l'application et de déclencher une alerte. Alertmanager reçoit ensuite cette alerte, tandis que Grafana permet de visualiser les métriques dans un dashboard.

L'environnement complet est orchestré avec Docker Compose.

## 🎯 Objectifs

- Mettre en place un environnement de monitoring.
- Exposer des métriques applicatives avec Python et Flask.
- Collecter les métriques avec Prometheus.
- Créer des règles d'alerte.
- Détecter l'indisponibilité d'une application.
- Transmettre les alertes à Alertmanager.
- Visualiser les métriques avec Grafana.
- Tester les scénarios de panne et de récupération.
- Orchestrer plusieurs services avec Docker Compose.

## 🏗️ Architecture

```text
                  Client HTTP
                      |
                      v
                +-----------+
                | Flask API |
                |   :5000   |
                +-----+-----+
                      |
                   /metrics
                      |
                      v
                +-----------+
                | Prometheus|
                |   :9090   |
                +-----+-----+
                      |
                 Alert Rules
                      |
                      v
               +--------------+
               | Alertmanager |
               |    :9093     |
               +--------------+

                +-----------+
                |  Grafana  |
                |   :3000   |
                +-----+-----+
                      |
                      v
                   Dashboard
```

## 📁 Structure du projet

```text
prometheus-alertmanager-monitoring/
│
├── app/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
│
├── prometheus/
│   ├── prometheus.yml
│   └── alerts.yml
│
├── alertmanager/
│   └── alertmanager.yml
│
├── grafana/
│   └── provisioning/
│       └── datasources/
│           └── datasource.yml
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 🌐 Application Flask

L'application expose les endpoints suivants :

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Vérifier le fonctionnement de l'application |
| `GET` | `/health` | Vérifier l'état de santé |
| `GET` | `/info` | Afficher les informations du projet |
| `GET` | `/metrics` | Exposer les métriques Prometheus |

### Tester l'API

```bash
curl http://localhost:5000/
curl http://localhost:5000/health
curl http://localhost:5000/info
```

Pour consulter les métriques :

```bash
curl http://localhost:5000/metrics
```

## 📊 Prometheus

Prometheus collecte les métriques de l'application Flask toutes les cinq secondes.

La configuration se trouve dans :

```text
prometheus/prometheus.yml
```

La cible de collecte est :

```yaml
scrape_configs:
  - job_name: "flask-api"
    static_configs:
      - targets:
          - "app:5000"
```

Le nom `app` correspond au service Flask défini dans Docker Compose.

Interface Prometheus :

http://localhost:9090

### Métriques principales

La métrique suivante compte les requêtes HTTP reçues par l'application :

```promql
app_requests_total
```

Pour vérifier la disponibilité de l'application :

```promql
up{job="flask-api"}
```

- `1` : Prometheus arrive à récupérer les métriques.
- `0` : Prometheus ne parvient plus à joindre la cible.

## 🚨 Règles d'alerte

Les règles sont définies dans :

```text
prometheus/alerts.yml
```

La règle principale est `ApplicationDown`.

```yaml
groups:
  - name: application-alerts
    rules:
      - alert: ApplicationDown
        expr: up{job="flask-api"} == 0
        for: 10s
        labels:
          severity: critical
        annotations:
          summary: "Flask application is down"
          description: "The Flask application has been unavailable for more than 10 seconds."
```

### Fonctionnement

1. Prometheus vérifie régulièrement la cible Flask.
2. Si la cible devient indisponible, la métrique `up` passe à `0`.
3. Si la condition persiste pendant dix secondes, l'alerte devient active.
4. Prometheus transmet l'alerte à Alertmanager.
5. Lorsque l'application revient et que la condition n'est plus vraie, l'alerte finit par être résolue.

Le délai réel dépend notamment de l'intervalle d'évaluation des règles et de collecte.

## 🔔 Alertmanager

Alertmanager reçoit les alertes envoyées par Prometheus.

Sa configuration se trouve dans :

```text
alertmanager/alertmanager.yml
```

Interface :

http://localhost:9093

Dans ce projet, Alertmanager est configuré avec un récepteur par défaut pour vérifier la réception des alertes.

Aucune notification par e-mail ou autre canal externe n'est configurée dans cette version.

## 📈 Grafana

Grafana permet de visualiser les métriques dans un dashboard.

Interface :

http://localhost:3000

La source de données Prometheus est configurée automatiquement grâce au fichier :

```text
grafana/provisioning/datasources/datasource.yml
```

L'URL utilisée entre les conteneurs est :

```text
http://prometheus:9090
```

### Dashboard

Le dashboard du projet est nommé :

`Application Monitoring & Alerts`

Les panneaux recommandés sont :

**1. Total des requêtes HTTP**

```promql
app_requests_total
```

**2. Taux de requêtes**

```promql
rate(app_requests_total[1m])
```

**3. Disponibilité de Flask**

```promql
up{job="flask-api"}
```

Pour le panneau de disponibilité :

- `1` indique que la cible est joignable.
- `0` indique que la cible est indisponible.

## 🐳 Docker Compose

Le projet utilise quatre services :

| Service | Port | Rôle |
|---|---:|---|
| Flask | `5000` | API et métriques |
| Prometheus | `9090` | Collecte et évaluation des règles |
| Alertmanager | `9093` | Gestion des alertes |
| Grafana | `3000` | Visualisation des métriques |

## 🚀 Installation

### 1. Prérequis

- Docker
- Docker Compose
- Git

### 2. Cloner le repository

```bash
git clone https://github.com/cis-debug/prometheus-alertmanager-monitoring.git
cd prometheus-alertmanager-monitoring
```

### 3. Construire l'application

```bash
docker compose build
```

### 4. Démarrer les services

```bash
docker compose up -d
```

### 5. Vérifier les conteneurs

```bash
docker compose ps
```

Les quatre services doivent être démarrés.

### 6. Accéder aux interfaces

- Flask : http://localhost:5000
- Prometheus : http://localhost:9090
- Alertmanager : http://localhost:9093
- Grafana : http://localhost:3000

Pour Grafana, utilise les identifiants définis lors de la configuration locale. Sur une installation neuve sans configuration personnalisée, les identifiants initiaux habituels sont `admin` / `admin`, avec une demande de changement de mot de passe.

## 🧪 Tester une alerte

### 1. Vérifier la disponibilité initiale

Dans Prometheus, exécuter :

```promql
up{job="flask-api"}
```

La valeur attendue est `1`.

### 2. Arrêter l'application

```bash
docker compose stop app
```

Attendre environ 15 à 20 secondes.

### 3. Vérifier l'alerte

Ouvrir :

http://localhost:9090/alerts

La règle `ApplicationDown` doit passer à l'état `FIRING` si la cible reste indisponible suffisamment longtemps.

Ouvrir ensuite :

http://localhost:9093

L'alerte doit être visible dans Alertmanager.

### 4. Redémarrer l'application

```bash
docker compose start app
```

Vérifier à nouveau :

```promql
up{job="flask-api"}
```

La valeur doit revenir à `1`. Après la prochaine collecte et l'évaluation des règles, l'alerte doit être résolue.

## 📈 Générer des requêtes de test

Pour envoyer vingt requêtes à l'application :

```bash
for i in {1..20}; do
  curl -s http://localhost:5000/ > /dev/null
done
```

Puis rechercher dans Prometheus :

```promql
app_requests_total
```

La valeur doit augmenter à mesure que l'application reçoit des requêtes.

## 🔧 Commandes utiles

Afficher les conteneurs :

```bash
docker compose ps
```

Consulter les logs Flask :

```bash
docker compose logs app
```

Consulter les logs Prometheus :

```bash
docker compose logs prometheus
```

Consulter les logs Alertmanager :

```bash
docker compose logs alertmanager
```

Consulter les logs Grafana :

```bash
docker compose logs grafana
```

Redémarrer les services :

```bash
docker compose restart
```

Reconstruire et redémarrer :

```bash
docker compose up -d --build
```

Arrêter les services :

```bash
docker compose down
```

## 🔐 Bonnes pratiques

- Ne pas publier de mots de passe, tokens ou secrets dans GitHub.
- Ne pas utiliser les identifiants par défaut dans un environnement exposé.
- Protéger les interfaces de monitoring en environnement réel.
- Utiliser des versions d'images maîtrisées plutôt que `latest` en production.
- Vérifier les règles et les configurations avant le déploiement.
- Configurer un canal de notification adapté aux besoins.
- Ajouter une surveillance des ressources et des erreurs applicatives.

## 🚀 Améliorations possibles

- Configurer des notifications par e-mail ou messagerie.
- Ajouter des alertes sur le taux d'erreurs HTTP.
- Surveiller le CPU, la mémoire et les conteneurs.
- Ajouter des métriques sur le temps de réponse.
- Provisionner automatiquement les dashboards Grafana.
- Ajouter des tests automatisés et une pipeline GitHub Actions.
- Déployer la stack dans un environnement cloud.


## 👩‍💻 Auteur

**Cisse Ndeye**

GitHub : https://github.com/cis-debug
