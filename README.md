# ImmoGest Sénégal 🏠

[![Déploiement Render](https://img.shields.io/badge/deploy-render-46E3B7)](https://render.com)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-3.1-lightgrey)](https://flask.palletsprojects.com)

**Plateforme professionnelle de gestion locative pour propriétaires au Sénégal**

---

## 📋 Fonctionnalités

- ✅ **Multi-biens** : Gérez plusieurs immeubles et appartements
- ✅ **Locataires** : Dossiers complets avec historique
- ✅ **Paiements** : Suivi des loyers et génération de quittances PDF
- ✅ **Dashboard** : Statistiques en temps réel (revenus, occupation, etc.)
- ✅ **Plans freemium** : Gratuit (2 appts), Standard (10 appts), Illimité
- ✅ **WhatsApp** : Support client intégré
- ✅ **Mobile-friendly** : Interface optimisée smartphone/tablette

---

## 🚀 Déploiement sur Render (Gratuit)

### Prérequis

- Compte GitHub
- Compte Render.com (gratuit)

### Étape 1 : Préparer le Repository

```bash
# Cloner le projet
git clone https://github.com/votre-username/immogest.git
cd immogest

# Créer un nouveau repo sur GitHub
# Puis push
git remote set-url origin https://github.com/VOTRE-USERNAME/immogest.git
git push -u origin main
```

### Étape 2 : Créer la Base de Données

1. Aller sur [dashboard.render.com](https://dashboard.render.com)
2. **New** → **PostgreSQL**
3. Configurer :
   - Name: `immogest_db`
   - Database: `immogest`
   - User: `immogest_user`
   - Region: `Frankfurt` (plus proche de l'Afrique)
   - Plan: **Free** 
4. **Create Database**
5. **Copier l'Internal Database URL** (commence par `postgresql://`)

### Étape 3 : Créer le Web Service

1. **New** → **Web Service**
2. **Connect GitHub** → Sélectionner `immogest`
3. Configurer :
   ```
   Name: immogest
   Region: Frankfurt (EU Central)
   Branch: main
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn run:app
   Plan: Free
   ```

4. **Variables d'environnement** (Advanced) :
   ```
   FLASK_ENV=production
   SECRET_KEY=<générer-une-clé-longue-et-aléatoire>
   DATABASE_URL=<coller-l-url-postgresql-copiée>
   ```

5. **Create Web Service**

### Étape 4 : Migrations Database

Une fois déployé, ouvrir le **Shell** dans Render :

```bash
flask db upgrade
```

### Étape 5 : Accéder à l'Application

Votre app est disponible sur :
```
https://immogest.onrender.com
```

---

## ⚙️ Configuration Locale (Développement)

### Installation

```bash
# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer dépendances
pip install -r requirements.txt
```

### Configuration

Créer `.env` :
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key-changez-moi
DATABASE_URL=sqlite:///instance/app.db
```

### Migrations

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Lancer

```bash
flask run --debug
```

App disponible sur `http://localhost:5000`

---

## 🗃️ Structure du Projet

```
immogest/
├── app/
│   ├── __init__.py           # Factory Flask
│   ├── models.py             # Modèles SQLAlchemy
│   ├── extensions.py         # Extensions (db, login_manager)
│   ├── blueprints/           # Blueprints Flask
│   │   ├── auth/             # Authentification
│   │   ├── properties/       # Immeubles & appartements
│   │   ├── finances/         # Paiements & PDF
│   │   └── main/             # Pages publiques
│   ├── templates/            # Templates Jinja2
│   └── static/               # CSS, images, JS
├── migrations/               # Alembic migrations
├── requirements.txt          # Dépendances Python
├── Procfile                  # Commande Render déploiement
├── render.yaml               # Config automated Render
├── .gitignore                # Fichiers à ignorer
└── run.py                    # Point d'entrée Flask
```

---

## 📊 Plans Tarifaires

| Plan | Apparts | Prix | Fonctionnalités |
|------|---------|------| ----------------|
| **Gratuit** | 2 | 0 FCFA | Dashboard basique, Quittances PDF |
| **Standard** | 10 | 5.000 FCFA/mois | + Stats avancées, Support prioritaire |
| **Illimité** | ∞ | 10.000 FCFA/mois | + Score performance, Formation incluse |

---

## 🛠️ Stack Technique

- **Backend** : Flask 3.1, SQLAlchemy, Flask-Login
- **Frontend** : Bootstrap 5, HTMX, Jinja2
- **Database** : PostgreSQL (prod), SQLite (dev)
- **PDF** : WeasyPrint
- **Déploiement** : Render.com (gratuit)

---

## 🔐 Sécurité

- ✅ Hashing passwords (Werkzeug)
- ✅ CSRF protection (Flask-WTF)
- ✅ Ownership checks sur toutes routes
- ✅ HTTPS automatique (Render SSL)
- ✅ Variables d'environnement sécurisées

---

## 📱 Support

- **WhatsApp** : +221 77 676 72 55
- **Email** : contact@immogest.sn
- **Issues GitHub** : [github.com/votre-repo/issues](https://github.com)

---

## 📄 Licence

© 2023 ImmoGest Sénégal. Tous droits réservés.

---

## 🙏 Contribution

Les contributions sont bienvenues ! 

1. Fork le projet
2. Créer une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Push (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrir une Pull Request

---

**Fait avec ❤️ au Sénégal**
