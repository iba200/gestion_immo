from flask import current_app, render_template, redirect, url_for, flash, make_response, request, abort
from flask_login import login_required, current_user
from app import db
from app.blueprints.finances import finances_bp
from app.blueprints.finances.forms import PaymentForm
from app.models import Tenant, Payment
import uuid
import os
import logging
from urllib.parse import quote

# Configuration du logging
logger = logging.getLogger(__name__)

# Gestion de l'erreur si WeasyPrint n'est pas installé
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    HTML = None
    WEASYPRINT_AVAILABLE = False
    logger.warning("WeasyPrint n'est pas installé. La génération de PDF sera désactivée.")


def _check_payment_access(payment):
    """
    Fonction utilitaire pour vérifier l'accès à un paiement.

    Args:
        payment: Instance de Payment

    Returns:
        bool: True si l'utilisateur a accès, False sinon
    """
    try:
        return payment.tenant.unit.property.owner == current_user
    except AttributeError:
        logger.error(f"Erreur lors de la vérification d'accès pour le paiement {payment.id}")
        return False


def _sanitize_phone_number(phone):
    """
    Nettoie et formate un numéro de téléphone pour WhatsApp.

    Args:
        phone: Numéro de téléphone brut

    Returns:
        str: Numéro nettoyé (seulement chiffres)
    """
    if not phone:
        return None
    # Supprime tous les caractères non-numériques sauf le + au début
    cleaned = ''.join(c for c in phone if c.isdigit() or (c == '+' and phone.index(c) == 0))
    return cleaned.replace('+', '')


@finances_bp.route('/pay/<int:tenant_id>', methods=['GET', 'POST'])
@login_required
def add_payment(tenant_id):
    """
    Enregistrer un nouveau paiement pour un locataire.

    Args:
        tenant_id: ID du locataire

    Returns:
        Template ou redirection
    """
    tenant = Tenant.query.get_or_404(tenant_id)

    # Sécurité : Vérifier que le locataire appartient à un immeuble du user
    if tenant.unit.property.owner != current_user:
        logger.warning(f"Tentative d'accès non autorisé au locataire {tenant_id} par l'utilisateur {current_user.id}")
        flash("Accès interdit.", "danger")
        return redirect(url_for('main.index'))

    form = PaymentForm()

    # Pré-remplissage du loyer si le champ est vide (seulement en GET)
    if request.method == 'GET' and not form.amount.data:
        form.amount.data = tenant.unit.rent_amount

    if form.validate_on_submit():
        try:
            # Création du paiement avec token unique
            payment = Payment(
                amount=form.amount.data,
                period=form.period.data,
                tenant=tenant,
                receipt_token=str(uuid.uuid4())
            )
            db.session.add(payment)
            db.session.commit()

            logger.info(f"Paiement créé: ID={payment.id}, Montant={payment.amount}, Locataire={tenant.full_name}")
            flash('Paiement enregistré avec succès !', 'success')

            # Redirection vers la page de succès avec options WhatsApp et PDF
            return redirect(url_for('finances.payment_success', payment_id=payment.id))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de l'enregistrement du paiement: {str(e)}")
            flash("Une erreur est survenue lors de l'enregistrement du paiement.", "danger")
            return redirect(url_for('finances.add_payment', tenant_id=tenant_id))

    return render_template('finances/add_payment.html', form=form, tenant=tenant)


@finances_bp.route('/success/<int:payment_id>')
@login_required
def payment_success(payment_id):
    """
    Page intermédiaire après enregistrement d'un paiement.
    Affiche le succès et propose l'envoi via WhatsApp.

    Args:
        payment_id: ID du paiement

    Returns:
        Template de succès
    """
    payment = Payment.query.get_or_404(payment_id)

    # Sécurité : Vérifier l'accès
    if not _check_payment_access(payment):
        logger.warning(f"Accès non autorisé au paiement {payment_id} par l'utilisateur {current_user.id}")
        flash("Accès interdit.", "danger")
        return redirect(url_for('main.index'))

    # Génération du lien de téléchargement PDF
    pdf_url = url_for('finances.download_receipt', payment_id=payment.id, _external=True)

    # Préparation du message WhatsApp
    month_label = payment.period  # Ex: "2023-11" ou "Novembre 2023"
    amount_fmt = "{:,.0f}".format(payment.amount).replace(',', ' ')

    # Message personnalisé
    msg_text = f"Bonjour {payment.tenant.full_name}, votre paiement de {amount_fmt} FCFA pour la période {month_label} a bien été reçu. Merci ! 🏠"

    # Encodage URL du message
    encoded_msg = quote(msg_text)

    # Si le locataire a un numéro de téléphone, on le préremplit
    if payment.tenant.phone:
        clean_phone = _sanitize_phone_number(payment.tenant.phone)
        if clean_phone:
            whatsapp_link = f"https://wa.me/{clean_phone}?text={encoded_msg}"
        else:
            whatsapp_link = f"https://wa.me/?text={encoded_msg}"
    else:
        whatsapp_link = f"https://wa.me/?text={encoded_msg}"

    return render_template('finances/success.html',
                         payment=payment,
                         whatsapp_link=whatsapp_link,
                         pdf_url=pdf_url)


@finances_bp.route('/receipt/download/<int:payment_id>')
@login_required
def download_receipt(payment_id):
    """
    Génération et téléchargement du reçu PDF pour un paiement.

    Args:
        payment_id: ID du paiement

    Returns:
        Réponse PDF ou redirection avec message d'erreur
    """
    payment = Payment.query.get_or_404(payment_id)

    # Sécurité : Vérifier l'accès
    if not _check_payment_access(payment):
        logger.warning(f"Tentative de téléchargement non autorisé du reçu {payment_id}")
        abort(403)

    # Vérifier que WeasyPrint est disponible
    if not WEASYPRINT_AVAILABLE or HTML is None:
        flash("Le module PDF (WeasyPrint) n'est pas installé sur le serveur.", "danger")
        return redirect(url_for('properties.tenant_details', tenant_id=payment.tenant.id))

    try:
        # 1. Génération du HTML à partir du template
       # Préparer les données pour le PDF
        owner = payment.tenant.unit.property.owner

        # Gestion du logo et de la couleur (Premium)
        logo_path = None
        brand_color = '#333333' # Couleur par défaut

        if owner.has_feature('custom_branding'):
            if owner.brand_color:
                brand_color = owner.brand_color

            if owner.logo_filename:
                # Chemin absolu pour WeasyPrint
                logo_path = os.path.join(current_app.root_path, 'static/uploads/logos', owner.logo_filename)
                # Vérifier si le fichier existe
                if not os.path.exists(logo_path):
                    logo_path = None

        rendered_html = render_template('pdf/receipt_template.html',
                              payment=payment,
                              property=payment.tenant.unit.property,
                              tenant=payment.tenant,
                              owner=owner,
                              logo_path=logo_path,
                              brand_color=brand_color)

        # 2. Transformation en PDF avec WeasyPrint
        pdf = HTML(string=rendered_html).write_pdf()
        try:
            logger.info(f"Début génération PDF pour paiement {payment_id}")
            if logo_path:
                logger.info(f"Logo path: {logo_path}")

            pdf = HTML(string=rendered_html).write_pdf()
            logger.info("PDF généré avec succès")
        except Exception as e:
            logger.error(f"Erreur WeasyPrint: {str(e)}")
            # Fallback sans logo si erreur
            if logo_path:
                logger.warning("Tentative de régénération sans logo")
                rendered_html = render_template('pdf/receipt_template.html',
                                      payment=payment,
                                      property=payment.tenant.unit.property,
                                      tenant=payment.tenant,
                                      owner=owner,
                                      logo_path=None,
                                      brand_color=brand_color)
                pdf = HTML(string=rendered_html).write_pdf()
            else:
                raise e

        # 3. Création de la réponse
        safe_name = payment.tenant.full_name.replace(' ', '_').replace('/', '-')
        filename = f"Quittance_{payment.period}_{safe_name}.pdf"

        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename="{filename}"'

        logger.info(f"Reçu PDF généré pour le paiement {payment_id}")
        return response

    except Exception as e:
        logger.error(f"Erreur génération PDF: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        flash("Une erreur est survenue lors de la génération du PDF.", "danger")
        return redirect(url_for('properties.tenant_details', tenant_id=payment.tenant.id))


@finances_bp.route('/payment/<int:payment_id>/delete', methods=['POST'])
@login_required
def delete_payment(payment_id):
    """
    Supprimer un paiement (en cas d'erreur de saisie).

    Args:
        payment_id: ID du paiement à supprimer

    Returns:
        Redirection vers la page du locataire
    """
    payment = Payment.query.get_or_404(payment_id)

    # Sécurité : Vérifier l'accès
    if not _check_payment_access(payment):
        logger.warning(f"Tentative de suppression non autorisée du paiement {payment_id}")
        flash("Accès interdit.", "danger")
        return redirect(url_for('properties.index'))

    tenant_id = payment.tenant.id
    payment_period = payment.period
    payment_amount = payment.amount

    try:
        db.session.delete(payment)
        db.session.commit()

        logger.info(f"Paiement supprimé: ID={payment_id}, Période={payment_period}, Montant={payment_amount}")
        flash(f'Paiement de {payment_amount} FCFA pour "{payment_period}" supprimé.', 'warning')

    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la suppression du paiement {payment_id}: {str(e)}")
        flash("Une erreur est survenue lors de la suppression du paiement.", "danger")

    return redirect(url_for('properties.tenant_details', tenant_id=tenant_id))


# ====== FONCTIONNALITÉS PREMIUM ======

@finances_bp.route('/export/excel')
@login_required
def export_excel():
    """
    Exporte tous les paiements de l'utilisateur vers un fichier Excel.
    Fonctionnalité réservée au plan Premium.
    """
    from app.decorators import feature_required
    from app.blueprints.finances.services import export_payments_to_excel
    from datetime import datetime
    from flask import send_file

    # Vérifier que l'utilisateur a accès à cette fonctionnalité
    if not current_user.has_feature('export_excel'):
        flash("🚀 Export Excel : fonctionnalité réservée au plan Premium !", "info")
        return redirect(url_for('main.pricing'))

    try:
        # Générer le fichier Excel (retourne un BytesIO)
        excel_file = export_payments_to_excel(current_user)

        # Réinitialiser le pointeur au début du fichier
        excel_file.seek(0)
        file_content = excel_file.getvalue()

        # Nom du fichier avec date
        filename = f"ImmoGest_Paiements_{datetime.now().strftime('%Y%m%d')}.xlsx"

        logger.info(f"Export Excel généré pour l'utilisateur {current_user.id} - Taille: {len(file_content)} bytes")

        # Créer la réponse manuellement pour un contrôle total des headers
        response = make_response(file_content)

        # Headers pour forcer le téléchargement (octet-stream est plus radical pour forcer le download)
        response.headers['Content-Type'] = 'application/octet-stream'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['Content-Length'] = len(file_content)

        # Headers pour éviter le cache (important si le navigateur a mis en cache la version texte)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

        return response

    except ImportError as e:
        logger.error(f"Erreur d'import lors de l'export Excel: {str(e)}")
        flash("Le module Excel n'est pas installé sur le serveur. Contactez le support.", "danger")
        return redirect(url_for('main.index'))
        flash("Une erreur est survenue lors de la génération du fichier Excel.", "danger")
        return redirect(url_for('main.index'))


@finances_bp.route('/reminders')
@login_required
def reminders():
    """
    Affiche la liste des locataires en retard de paiement pour le mois en cours.
    Fonctionnalité Premium.
    """
    from app.decorators import feature_required
    from app.blueprints.finances.services import get_late_tenants
    from datetime import datetime

    # Vérifier que l'utilisateur a accès à cette fonctionnalité
    if not current_user.has_feature('payment_reminders'):
        flash("🚀 Rappels automatiques : fonctionnalité réservée au plan Premium !", "info")
        return redirect(url_for('main.pricing'))

    # Récupérer les locataires en retard
    late_tenants = get_late_tenants(current_user)
    current_period = datetime.now().strftime('%Y-%m')

    return render_template('finances/reminders.html',
                          late_tenants=late_tenants,
                          current_period=current_period)


@finances_bp.route('/reminders/send/<int:tenant_id>')
@login_required
def send_reminder(tenant_id):
    """
    Redirige vers WhatsApp pour envoyer un rappel.
    """
    from app.blueprints.finances.services import send_whatsapp_reminder
    from datetime import datetime

    tenant = Tenant.query.get_or_404(tenant_id)

    # Sécurité
    if tenant.unit.property.owner != current_user:
        flash("Accès interdit.", "danger")
        return redirect(url_for('finances.reminders'))

    # Générer le lien WhatsApp
    current_period = datetime.now().strftime('%Y-%m')
    whatsapp_url = send_whatsapp_reminder(tenant, tenant.unit.rent_amount, current_period)

    # Redirection vers WhatsApp
    return redirect(whatsapp_url)

