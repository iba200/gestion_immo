from flask import render_template
from app.models import Property, Unit, Tenant
from flask_login import login_required, current_user

from app.blueprints.main import main_bp
from app import db
from app.models import User
from app.decorators import admin_required
from flask import request, redirect, url_for, flash
from datetime import datetime, timedelta # Import important !




@main_bp.route('/')
def index():
    # CAS 1 : L'utilisateur est connecté -> On affiche ses STATISTIQUES
    if current_user.is_authenticated:
        # 1. Total des immeubles
        total_properties = current_user.properties.count()

        # 2. Total des appartements (on doit boucler ou faire une jointure)
        # Pour faire simple et efficace en Python :
        all_units = []
        for prop in current_user.properties:
            all_units.extend(prop.units.all())
        total_units = len(all_units)

        # 3. Appartements occupés vs Vacants
        occupied_units = sum(1 for u in all_units if u.current_tenant)
        vacant_units = total_units - occupied_units

        # 4. Taux d'occupation (pour la barre de progression)
        occupancy_rate = 0
        if total_units > 0:
            occupancy_rate = round((occupied_units / total_units) * 100)

        # 5. Revenus mensuels théoriques (Somme des loyers des apparts occupés)
        monthly_potential = sum(u.rent_amount for u in all_units if u.current_tenant)
        
        # 6. Statistiques Premium (si l'utilisateur a la fonctionnalité analytics)
        premium_stats = None
        if current_user.has_feature('analytics_dashboard'):
            from app.blueprints.finances.services import get_payment_statistics
            premium_stats = get_payment_statistics(current_user)

        return render_template('index_dashboard.html',
                               total_properties=total_properties,
                               total_units=total_units,
                               occupied_units=occupied_units,
                               vacant_units=vacant_units,
                               occupancy_rate=occupancy_rate,
                               monthly_potential=monthly_potential,
                               premium_stats=premium_stats)

    # CAS 2 : Visiteur anonyme -> On affiche la LANDING PAGE
    else:
        return render_template('index_landing.html')


@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """
    Page de paramètres pour la personnalisation (Logo, Couleurs).
    Accessible à tous, mais les fonctionnalités dépendent du plan.
    """
    import os
    from werkzeug.utils import secure_filename
    from flask import current_app
    
    if request.method == 'POST':
        # Debug logs
        print(f"DEBUG: POST settings received. User plan: {current_user.plan}")
        print(f"DEBUG: Files: {request.files}")
        print(f"DEBUG: Form: {request.form}")
        
        # 1. Mise à jour de la couleur (Premium uniquement)
        if current_user.has_feature('custom_branding'):
            brand_color = request.form.get('brand_color')
            if brand_color:
                print(f"DEBUG: Updating brand color to {brand_color}")
                current_user.brand_color = brand_color
                
            # 2. Upload du Logo (Premium uniquement)
            if 'logo' in request.files:
                file = request.files['logo']
                print(f"DEBUG: Logo file received: {file.filename}")
                
                if file and file.filename != '':
                    # Vérifier extension
                    allowed_extensions = {'png', 'jpg', 'jpeg'}
                    if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                        # Créer le dossier s'il n'existe pas
                        upload_folder = os.path.join(current_app.root_path, 'static/uploads/logos')
                        os.makedirs(upload_folder, exist_ok=True)
                        print(f"DEBUG: Upload folder: {upload_folder}")
                        
                        # Nom sécurisé et unique
                        filename = secure_filename(f"logo_{current_user.id}_{int(datetime.now().timestamp())}.{file.filename.rsplit('.', 1)[1].lower()}")
                        save_path = os.path.join(upload_folder, filename)
                        print(f"DEBUG: Saving logo to {save_path}")
                        
                        file.save(save_path)
                        
                        # Supprimer l'ancien logo si existant
                        if current_user.logo_filename:
                            old_path = os.path.join(upload_folder, current_user.logo_filename)
                            if os.path.exists(old_path):
                                os.remove(old_path)
                                
                        current_user.logo_filename = filename
                    else:
                        print("DEBUG: Invalid file extension")
                        flash("Format de logo invalide. Utilisez PNG ou JPG.", "danger")
        else:
            print("DEBUG: User does not have custom_branding feature")
            flash("Fonctionnalité réservée au plan Premium.", "warning")
        
        # Sauvegarder les changements
        try:
            db.session.commit()
            print("DEBUG: Changes committed to DB")
            flash("Vos paramètres ont été mis à jour avec succès ! ✨", "success")
        except Exception as e:
            db.session.rollback()
            print(f"DEBUG: Error saving to DB: {e}")
            flash("Une erreur est survenue lors de la sauvegarde.", "danger")
            
        return redirect(url_for('main.settings'))
        
    return render_template('settings.html')

@main_bp.route('/pricing')
def pricing():
    return render_template('pricing.html')


# 1. Tableau de bord Super Admin
@main_bp.route('/admin/users')
@login_required
@admin_required
def admin_dashboard():
    # On récupère tous les utilisateurs, du plus récent au plus ancien
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users, now=datetime.utcnow())

# 2. Action pour changer le plan d'un utilisateur

@main_bp.route('/admin/users/<int:user_id>/update_plan', methods=['POST'])
@login_required
@admin_required
def update_user_plan(user_id):
    user = User.query.get_or_404(user_id)
    action = request.form.get('action') # On récupère l'action (1 mois, 1 an, Stop)

    if action == 'free':
        user.plan = 'free'
        user.subscription_end = None # On annule les dates
        flash(f'{user.email} est repassé en Gratuit.', 'info')

    elif action == 'standard_1_month':
        user.plan = 'standard'
        # On ajoute 30 jours à partir de maintenant (ou on prolonge s'il lui restait du temps)
        start_date = user.subscription_end if (user.subscription_end and user.subscription_end > datetime.utcnow()) else datetime.utcnow()
        user.subscription_end = start_date + timedelta(days=30)
        flash(f'Standard activé pour 1 mois (jusqu\'au {user.subscription_end.strftime("%d/%m/%Y")})', 'success')

    elif action == 'premium_1_month':
        user.plan = 'premium'
        start_date = user.subscription_end if (user.subscription_end and user.subscription_end > datetime.utcnow()) else datetime.utcnow()
        user.subscription_end = start_date + timedelta(days=30)
        flash(f'Premium activé pour 1 mois.', 'success')

    elif action == 'premium_1_year':
        user.plan = 'premium'
        start_date = user.subscription_end if (user.subscription_end and user.subscription_end > datetime.utcnow()) else datetime.utcnow()
        user.subscription_end = start_date + timedelta(days=365)
        flash(f'Premium activé pour 1 AN ! Cashflow sécurisé.', 'success')

    db.session.commit()
    return redirect(url_for('main.admin_dashboard'))
