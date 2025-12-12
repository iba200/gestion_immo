# Cahier des Charges Frontend — Version Minimaliste Premium (Style Apple / Airbnb)

Ce document décrit **toutes les pages**, **composants**, **interactions** et **règles UI** de ton SaaS ImmoGest Sénégal en respectant le style que tu veux:

**minimaliste, premium, ultra-épuré, typographie Inter, 1 couleur d'accent, animations légères.**

Aucun élément inutile. Tout est clair, respiré, haut de gamme.

---

# 1. Principes de Design

## 1.1 Identité visuelle

* **Palette minimale (3 couleurs)** :

  * Blanc (#FFFFFF)
  * Noir profond (#0A0A0A)
  * Bleu Accent (#2563EB)
* **Typographie principale:** Inter, 400 / 500 / 600
* **Rayon de bordure:** 8px
* **Ombre très légère:** rgba(0,0,0,0.04)
* **Icônes fines:** Bootstrap Icons

## 1.2 Style général

* Pas d’éléments superflus
* Pas de bordures épaisses
* Espaces généreux
* Composants aérés
* Animations douces (opacity, scale 0.98→1, 150ms)
* Layout 100% responsive mobile-first
* Navigation mobile avec un **bottom bar minimaliste**

---

# 2. Pages du SaaS

## 2.1 Landing Page (optionnelle mais recommandée)

Objectif : convaincre, montrer la simplicité, rassurer.

### Sections

1. **Hero minimaliste**

   * Titre large : "Gérez vos biens immobiliers en toute simplicité"
   * Sous-texte : "Une plateforme professionnelle, pensée pour les propriétaires au Sénégal."
   * Bouton primaire bleu

2. **Fonctionnalités clés** (cartes très légères)

   * Gestion des immeubles
   * Quittances PDF
   * Dashboard en temps réel

3. **Capture d’écran du dashboard** style Apple (clean, fond arrondi, ombre douce)

4. **Plans tarifaires** en 3 colonnes minimalistes

5. **Footer** simple: contact + mentions

---

## 2.2 Page Login / Register

### Login

* Formulaire centré, carte blanche ultra clean
* 2 champs + bouton
* Lien "Créer un compte"
* Logo minimal en haut

### Register

* Même structure
* Champs : email, téléphone, mot de passe
* Indications discrètes

---

## 2.3 Dashboard Principal

Style très épuré, façon Airbnb pour l’air, Apple pour la précision.

### Contenu

* **Header simple** : Bonjour, Nom

* **Cards KPI minimalistes** :

  * Revenus du mois
  * Taux d’occupation
  * Appartements vides

* **Liste des immeubles** sous forme de cartes blanches arrondies

  * Nom immeuble
  * Nombre d’apparts
  * Occupation

### Interactions

* Animations hover très légères
* Icônes simples

---

## 2.4 Page Immeubles (liste)

* Liste verticale de cartes très épurées
* Toujours fond blanc + shadow 0.04
* Bouton bleu en haut "Ajouter Immeuble"

### Carte immeuble

* Nom
* Adresse
* Statistiques
* Flèche → détail

---

## 2.5 Page Détail Immeuble

* Grand titre
* Mini-statistiques en haut
* Section Appartements

### Appartements en liste

* Une carte simple par appartement

  * Porte (A1, B2…)
  * Loyer
  * État: occupé / vide (pastille colorée)

* Bouton “Ajouter un appartement” sticky en bas sur mobile

---

## 2.6 Page Détail Appartement

### Si vide

* Carte blanche “Aucun locataire”
* Bouton "Ajouter un locataire"

### Si occupé

* Carte Locataire minimaliste

  * Nom + téléphone
  * Statut paiement
* Historique des paiements en liste épurée
* Bouton “Enregistrer un paiement” en bas

---

## 2.7 Page Ajout Locataire

* Formulaire simple vertical
* Layout mobile-first très respiré
* Aucun décor inutile

---

## 2.8 Page Enregistrement Paiement

* Formulaire minimal
* Montant pré-rempli
* Dropdown mois
* Bouton bleu
* Message de succès non intrusif

---

## 2.9 Page Quittance PDF (preview si prévue)

* Affichage ultra clean façon facture Apple
* Espacements larges, typographie nette

---

# 3. Composants UI

## 3.1 Cards

* Fond blanc
* ombre 0 1px 4px rgba(0,0,0,0.04)
* padding 20px
* arrondi 10px

## 3.2 Boutons

* **Primaire bleu plein**
* **Secondaire blanc** avec légère bordure gris clair
* Taille : 44px hauteur
* Arrondi : 8px

## 3.3 Navigation Mobile

Barre inférieure minimaliste :

* Dashboard
* Immeubles
* Apparts
* Profil

Icônes fines + étiquette 12px

---

# 4. Règles d’UX

* Toujours favoriser la lisibilité
* Les actions importantes doivent être bleu accent
* Les cartes sont toujours espacées
* Pas plus de 1 niveau de hiérarchie par page
* Désactiver les décorations superflues
* Feedback utilisateur simple :

  * vert léger pour succès
  * rouge doux pour erreur

---

# 5. Pages Profil & Paramètres

* Informations du propriétaire
* Changer email / téléphone
* Paramètres du compte
* Bouton “Supprimer compte” discret

---

# 6. Plans Tarifaires (dans app)

Version ultra simple :

* 3 cartes
* Titre, prix, features
* Bouton bleu

---

# 7. Footer (web seulement)

* Logo minimal
* Mentions légales
* Contact email

---

# 8. Accessibilité & Performance

* Contraste AA
* HTML sémantique
* Chargement < 2 secondes
* Images optimisées 80%
* Police Inter chargée en swap

---

Ce cahier reflète exactement ton style minimaliste premium, sans rien de superflu, parfaitement aligné avec le SaaS ImmoGest Sénégal.
