# README – Mini-système de collecte de données Shelly Pro 1PM

## 📌 Description

Ce projet implémente un système complet de collecte, transmission, stockage et visualisation en temps réel des données issues des bornes de recharge **Shelly Pro 1PM**. Il comprend :

* Un **webhook** acceptant GET et POST
* Une **intégration Kafka** pour la diffusion des données
* Un **stockage PostgreSQL** persistant
* Une **interface web temps réel** pour visualiser les mesures
* Une **API REST** pour l’accès programmatique aux données

L’architecture repose sur **Django** et **Django REST Framework**, avec conteneurisation **Docker**.

---

## ⚙️ Prérequis

* **Docker** ≥ 20.10
* **Docker Compose** ≥ 1.29
* Un **cluster Kafka** accessible (local ou externe)
* PostgreSQL (lancé via docker-compose)

---

## 🚀 Installation et Lancement

1. **Cloner le projet** :

   ```bash
   git clone <repo_url>
   cd <repo_name>
   ```

2. **Configurer les variables d’environnement** :

   * Copier le fichier `.env-sample` en `.env`
   * Modifier les valeurs selon vos besoins (DB, Kafka, seuil d’alerte, etc.)

   Exemple minimal :

   ```env
   POSTGRES_DB=shelly
   POSTGRES_USER=shelly
   POSTGRES_PASSWORD=secret
   POSTGRES_HOST=db
   POSTGRES_PORT=5432

   KAFKA_BROKER=localhost:9092
   KAFKA_TOPIC=shelly_data

   ALERT_THRESHOLD=3500
   ```

3. **Construire et démarrer les conteneurs** :

   ```bash
   docker-compose up --build
   ```

4. Les migrations Django sont appliquées automatiquement via `entrypoint.sh`.

---

## 📡 Webhook

L’endpoint `/webhook` accepte deux formats d’entrée :

### 1. POST JSON

```bash
curl -X POST http://localhost:8000/webhook/ \
  -H "Content-Type: application/json" \
  -d '{"power": 120.5, "voltage": 230.1, "current": 0.52, "energy": 10.2}'
```

### 2. GET Query String

```bash
curl "http://localhost:8000/webhook/?power=100.3&voltage=230.0&current=0.43&energy=8.9"
```

👉 Dans les deux cas, un champ `timestamp` est ajouté automatiquement côté serveur.

---

## 📊 Kafka

* Chaque mesure reçue est envoyée dans **Kafka** au format JSON.
* Le topic utilisé est défini dans `.env` (`KAFKA_TOPIC=shelly_data`).
* Exemple de message produit :

```json
{
  "power": 120.5,
  "voltage": 230.1,
  "current": 0.52,
  "energy": 10.2,
  "timestamp": "2025-09-01T09:30:00Z"
}
```

---

## 🗄 Stockage PostgreSQL

Les mesures sont stockées dans la table `measurement` avec le modèle :

* `power` (float)
* `voltage` (float)
* `current` (float)
* `energy` (float)
* `timestamp` (datetime)

Les migrations créent la structure automatiquement.

---

## 📺 Interface Web Temps Réel

Accessible à l’adresse :

```
http://localhost:8000
```

Fonctionnalités :

* Affichage des **10 dernières mesures**
* Rafraîchissement automatique toutes les 2 secondes
* **Alerte visuelle** si la puissance dépasse le seuil défini (`ALERT_THRESHOLD`)
* Graphiques interactifs (consommation dans le temps)

---

## 🔌 API REST

API basée sur Django REST Framework, disponible sous `/api/measurements/`.

### 1. Liste paginée des mesures

```bash
GET http://localhost:8000/api/measurements/
```

### 2. Dernières 10 mesures

```bash
GET http://localhost:8000/api/measurements/latest/
```

### 3. Filtrage par période

```bash
GET http://localhost:8000/api/measurements/?start=2025-09-01T00:00:00Z&end=2025-09-01T23:59:59Z
```

---

## 📂 Structure du projet

```
SHELLY_PROJECT/
│
├── measurements/                # Application principale Django (gestion des mesures)
│   ├── migrations/              # Migrations de la base de données
│   ├── templates/               # Templates HTML pour l'affichage web
│   ├── __init__.py
│   ├── admin.py                 # Configuration de l’admin Django
│   ├── apps.py                  # Configuration de l’app Django
│   ├── kafka_producer.py        # Producteur Kafka (envoi des mesures)
│   ├── models.py                # Modèle Measurement
│   ├── serializers.py           # Sérialiseurs pour l’API REST
│   ├── tests.py                 # Tests unitaires
│   ├── urls.py                  # Routes spécifiques à l’app
│   └── views.py                 # Logique des endpoints (webhook, API, affichage)
│
├── shelly_project/              # Répertoire principal Django (projet)
│   ├── __init__.py
│   ├── asgi.py                  # Configuration ASGI
│   ├── settings.py              # Paramètres globaux Django (Postgres, Kafka, etc.)
│   ├── urls.py                  # Routes globales du projet
│   └── wsgi.py                  # Configuration WSGI
│
├── .env                         # Variables d’environnement locales (non versionné)
├── .env-sample                  # Exemple de configuration .env
├── docker-compose.yml           # Orchestration des services (web, Postgres, Kafka)
├── Dockerfile                   # Image Docker pour le service web
├── entrypoint.sh                # Script d’initialisation (migrations, wait-for-db)
├── manage.py                    # Script principal Django
└── README.md                    # Documentation du projet
```

---

## 🎯 Exemples de scénarios réels

1. **Borne envoie 3500 W** → une alerte rouge s’affiche sur l’UI.
2. **Consultation historique** → l’API REST permet de filtrer par plage de dates pour analyser la consommation.
3. **Intégration externe** → Kafka diffuse les mesures en temps réel pour une autre application de monitoring.

---

## ✅ Tests rapides

1. Démarrer l’application avec `docker-compose up`.
2. Envoyer une requête au webhook (`POST` ou `GET`).
3. Vérifier :

   * Le message apparaît dans Kafka (`shelly_data`).
   * La donnée est stockée dans PostgreSQL.
   * L’interface web affiche la mesure.
   * L’API REST retourne la mesure.

---

## 👤 Auteur

Développé par Aymen – 2025.
