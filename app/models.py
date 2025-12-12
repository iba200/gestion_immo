from datetime import datetime
import uuid
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager

# 1. Gestionnaire de chargement utilisateur pour Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 2. Modèle Propriétaire (User)
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True) # Format local ex: 77 123 45 67
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    plan = db.Column(db.String(20), default='free')

    # Relation : Un propriétaire a plusieurs immeubles
    properties = db.relationship('Property', backref='owner', lazy='dynamic', cascade="all, delete-orphan")

    # NOUVEAU CHAMP : Date de fin d'abonnement
    subscription_end = db.Column(db.DateTime, nullable=True)

    # Personnalisation (Premium)
    logo_filename = db.Column(db.String(255), nullable=True)
    brand_color = db.Column(db.String(7), default='#4F46E5') # Couleur par défaut (Indigo)

    def get_total_units(self):
        """Retourne le nombre total d'appartements possédés"""
        count = 0
        for prop in self.properties:
            count += prop.units.count()
        return count
    
    def get_unit_limit(self):
        """Retourne la limite d'appartements selon le plan actif"""
        # Vérifier si l'abonnement est expiré
        if self.plan in ['standard', 'premium'] and self.subscription_end:
            if datetime.utcnow() > self.subscription_end:
                return 2  # Retour au plan Free si expiré
        
        # Limites par plan
        limits = {
            'free': 2,
            'standard': 10,
            'premium': float('inf')  # Illimité
        }
        return limits.get(self.plan, 2)
    
    def can_add_unit(self):
        """Vérifie si l'utilisateur peut ajouter un appartement"""
        limit = self.get_unit_limit()
        if limit == float('inf'):
            return True
        return self.get_total_units() < limit
    
    def can_add_property(self):
        """Vérifie si l'utilisateur peut ajouter un immeuble (Free = 1 seul immeuble)"""
        # Vérifier si l'abonnement est expiré
        if self.plan in ['standard', 'premium'] and self.subscription_end:
            if datetime.utcnow() > self.subscription_end:
                return self.properties.count() < 1  # Free = 1 immeuble max
        
        if self.plan == 'free':
            return self.properties.count() < 1
        return True  # Standard et Premium = illimité
    
    def has_feature(self, feature_name):
        """Vérifie si une fonctionnalité est disponible pour le plan de l'utilisateur"""
        # Vérifier si l'abonnement est expiré pour les plans payants
        active_plan = self.plan
        if self.plan in ['standard', 'premium'] and self.subscription_end:
            if datetime.utcnow() > self.subscription_end:
                active_plan = 'free'  # Retour au plan Free
        
        # Définition des fonctionnalités par plan
        features = {
            'free': ['basic_stats', 'pdf_receipts', 'tenant_management'],
            'standard': ['basic_stats', 'pdf_receipts', 'tenant_management', 
                        'advanced_stats', 'multi_properties', 'whatsapp_support'],
            'premium': ['basic_stats', 'pdf_receipts', 'tenant_management',
                       'advanced_stats', 'multi_properties', 'whatsapp_support',
                       'auto_whatsapp', 'payment_reminders', 'export_excel',
                       'analytics_dashboard', 'custom_branding', 'multi_users',
                       'priority_support']
        }
        
        plan_features = features.get(active_plan, [])
        return feature_name in plan_features

    @property
    def is_subscription_active(self):
        """Petite aide pour l'affichage dans le template"""
        if self.plan == 'free': return True # Le plan gratuit est toujours actif
        if not self.subscription_end: return False
        return datetime.utcnow() < self.subscription_end

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

    @property
    def plan_display_name(self):
        """Affiche le nom joli du plan"""
        if self.plan == 'standard': return 'Standard'
        if self.plan == 'premium': return 'Premium Illimité'
        return 'Gratuit (Découverte)'


# 3. Modèle Immeuble (Property)
class Property(db.Model):
    __tablename__ = 'properties'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # Ex: "Immeuble Keur Massar"
    address = db.Column(db.String(200), nullable=True)

    # Clé étrangère vers le propriétaire
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relation : Un immeuble a plusieurs appartements
    units = db.relationship('Unit', backref='property', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Property {self.name}>'

# 4. Modèle Appartement (Unit)
class Unit(db.Model):
    __tablename__ = 'units'

    id = db.Column(db.Integer, primary_key=True)
    door_number = db.Column(db.String(20), nullable=False) # Ex: "A1", "2ème Gauche"
    rent_amount = db.Column(db.Float, nullable=False) # Montant du loyer en CFA

    # Clé étrangère vers l'immeuble
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)

    # Relation : Un appartement peut avoir un historique de locataires
    # CASCADE DELETE: quand on supprime un appartement, on supprime aussi ses locataires
    tenants = db.relationship('Tenant', backref='unit', lazy='dynamic', cascade="all, delete-orphan")

    @property
    def current_tenant(self):
        """Retourne le locataire actif (celui qui n'est pas parti)"""
        return self.tenants.filter_by(is_active=True).first()

    def __repr__(self):
        return f'<Unit {self.door_number} - {self.rent_amount} CFA>'

# 5. Modèle Locataire (Tenant)
class Tenant(db.Model):
    __tablename__ = 'tenants'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True)

    is_active = db.Column(db.Boolean, default=True) # True = Habite encore là
    entry_date = db.Column(db.Date, default=datetime.utcnow)

    # Clé étrangère vers l'appartement
    unit_id = db.Column(db.Integer, db.ForeignKey('units.id'), nullable=False)

    # Relation : Un locataire effectue plusieurs paiements
    # CASCADE DELETE: quand on supprime un locataire, on supprime aussi ses paiements
    payments = db.relationship('Payment', backref='tenant', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Tenant {self.full_name}>'


# 6. Modèle Paiement (Payment)
class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date_paid = db.Column(db.DateTime, default=datetime.utcnow)
    period = db.Column(db.String(7), nullable=False) # Format "YYYY-MM"
    receipt_token = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    
    # Nouveaux champs pour fonctionnalités Premium
    whatsapp_sent = db.Column(db.Boolean, default=False)  # Quittance envoyée via WhatsApp auto
    reminder_sent = db.Column(db.Boolean, default=False)  # Rappel envoyé

    # Clé étrangère vers le locataire
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    def is_overdue(self, days=5):
        """Détermine si un paiement est en retard (par défaut 5 jours après la période)"""
        from dateutil.relativedelta import relativedelta
        
        # Convertir la période ("2023-11") en date
        try:
            year, month = map(int, self.period.split('-'))
            period_date = datetime(year, month, 1)
            # Ajouter 1 mois + X jours de grâce
            due_date = period_date + relativedelta(months=1, days=days)
            return datetime.utcnow() > due_date
        except:
            return False

    def __repr__(self):
        return f'<Payment {self.amount} CFA - {self.period}>'
