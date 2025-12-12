# Documentation des Routes de l'Application

Ce document liste toutes les routes disponibles dans l'application **ImmoGest SaaS**, organisées par module (Blueprint).

## 1. Module Principal (`main`)
Gère les pages publiques, le tableau de bord et l'administration.

| Méthode | URL | Fonction | Description | Accès | Variables Template |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | `index` | Affiche le **Tableau de Bord** (si connecté) ou la **Landing Page** (si anonyme). | Public / Auth | `total_properties`, `total_units`, `occupied_units`, `vacant_units`, `occupancy_rate`, `monthly_potential` (Dashboard) |
| `GET` | `/pricing` | `pricing` | Affiche la page des tarifs. | Public | - |
| `GET` | `/admin/users` | `admin_dashboard` | Tableau de bord Super Admin (liste des utilisateurs). | Admin | `users`, `now` |
| `POST` | `/admin/users/<id>/update_plan` | `update_user_plan` | Modifie le plan d'abonnement d'un utilisateur. | Admin | - (Redirection) |

## 2. Module Authentification (`auth`)
Gère la connexion, l'inscription et la déconnexion.

| Méthode | URL | Fonction | Description | Accès | Variables Template |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET`, `POST` | `/auth/login` | `login` | Page de connexion. | Public | `form` |
| `GET`, `POST` | `/auth/register` | `register` | Page d'inscription. | Public | `form` |
| `GET` | `/auth/logout` | `logout` | Déconnecte l'utilisateur et redirige vers la connexion. | Auth | - (Redirection) |

## 3. Module Propriétés (`properties`)
Gère les immeubles, les appartements et les locataires.

| Méthode | URL | Fonction | Description | Accès | Variables Template |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/properties/` | `index` | Liste tous les immeubles du propriétaire connecté. | Auth | `properties` |
| `GET`, `POST` | `/properties/add` | `add` | Formulaire pour ajouter un nouvel immeuble. | Auth | `form` |
| `GET` | `/properties/<id>` | `details` | Affiche les détails d'un immeuble et la liste de ses appartements. | Auth | `property`, `units` |
| `GET`, `POST` | `/properties/<id>/add_unit` | `add_unit` | Ajoute un appartement à un immeuble spécifique. | Auth | `form`, `property` |
| `GET`, `POST` | `/properties/unit/<id>/new_tenant` | `new_tenant` | Ajoute un locataire à un appartement (si vacant). | Auth | `form`, `unit` |
| `GET` | `/properties/tenant/<id>` | `tenant_details` | Affiche le dossier d'un locataire et son historique de paiements. | Auth | `tenant`, `payments` |

## 4. Module Finances (`finances`)
Gère les paiements et les quittances.

| Méthode | URL | Fonction | Description | Accès | Variables Template |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET`, `POST` | `/finances/pay/<tenant_id>` | `add_payment` | Enregistre un nouveau paiement pour un locataire. | Auth | `form`, `tenant` |
| `GET` | `/finances/receipt/<payment_id>` | `receipt` | Génère et télécharge la **Quittance de Loyer (PDF)**. | Auth | `payment`, `tenant`, `owner`, `property` |
