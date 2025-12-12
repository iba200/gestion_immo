from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """
    Décorateur pour restreindre l'accès aux administrateurs uniquement.
    Usage: @admin_required
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Vous devez être connecté pour accéder à cette page.", "danger")
            return redirect(url_for('auth.login'))
        
        if current_user.email != 'admin@immogest.com':  # À adapter selon votre logique
            flash("Accès réservé aux administrateurs.", "danger")
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def plan_required(min_plan):
    """
    Décorateur pour restreindre l'accès selon le plan d'abonnement.
    
    Usage:
        @plan_required('standard')  # Exige Standard minimum
        @plan_required('premium')   # Exige Premium
    
    Args:
        min_plan: 'standard' ou 'premium'
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Vous devez être connecté.", "danger")
                return redirect(url_for('auth.login'))
            
            # Hiérarchie des plans
            plan_hierarchy = {'free': 0, 'standard': 1, 'premium': 2}
            
            # Vérifier si l'abonnement est expiré
            user_plan = current_user.plan
            if current_user.plan in ['standard', 'premium'] and current_user.subscription_end:
                from datetime import datetime
                if datetime.utcnow() > current_user.subscription_end:
                    user_plan = 'free'  # Abonnement expiré
            
            current_level = plan_hierarchy.get(user_plan, 0)
            required_level = plan_hierarchy.get(min_plan, 0)
            
            if current_level < required_level:
                plan_names = {'standard': 'Standard', 'premium': 'Premium'}
                flash(f"Cette fonctionnalité nécessite le plan {plan_names.get(min_plan, min_plan)}. "
                      f"Passez à l'étape supérieure !", "warning")
                return redirect(url_for('main.pricing'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def feature_required(feature_name):
    """
    Décorateur pour restreindre l'accès selon les fonctionnalités disponibles.
    
    Usage:
        @feature_required('export_excel')
        @feature_required('auto_whatsapp')
    
    Args:
        feature_name: Nom de la fonctionnalité à vérifier
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Vous devez être connecté.", "danger")
                return redirect(url_for('auth.login'))
            
            if not current_user.has_feature(feature_name):
                # Messages personnalisés selon la fonctionnalité
                messages = {
                    'export_excel': "Export Excel réservé au plan Premium",
                    'auto_whatsapp': "Envoi automatique WhatsApp : fonctionnalité Premium",
                    'payment_reminders': "Rappels automatiques : fonctionnalité Premium",
                    'analytics_dashboard': "Dashboard analytique : disponible en Premium",
                    'custom_pdf': "Personnalisation PDF : fonctionnalité Premium",
                    'multi_users': "Multi-utilisateurs : fonctionnalité Premium",
                }
                
                message = messages.get(feature_name, f"Cette fonctionnalité n'est pas disponible dans votre plan")
                flash(f"🚀 {message}. Passez au Premium !", "info")
                return redirect(url_for('main.pricing'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
