from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.blueprints.properties import properties_bp
from app.blueprints.properties.forms import PropertyForm
from app.models import Property
from app.blueprints.properties.forms import UnitForm, TenantForm
from app.models import Unit, Tenant, Payment # Importez le modèle Unit


@properties_bp.route('/')
@login_required
def index():
    # On récupère uniquement les immeubles du propriétaire connecté
    properties = current_user.properties.all()
    return render_template('properties/index.html', properties=properties)

@properties_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    # Restriction: Plan Free = 1 seul immeuble
    if not current_user.can_add_property():
        flash(f"🏠 Plan {current_user.plan_display_name} : 1 seul immeuble autorisé. "
              f"Passez au plan Standard pour gérer plusieurs immeubles !", "warning")
        return redirect(url_for('main.pricing'))
    
    form = PropertyForm()
    if form.validate_on_submit():
        # Création de l'objet Immeuble
        new_property = Property(
            name=form.name.data,
            address=form.address.data,
            owner=current_user # On lie l'immeuble au user connecté (magie de SQLAlchemy)
        )
        db.session.add(new_property)
        db.session.commit()
        flash(f'Immeuble "{new_property.name}" ajouté avec succès !', 'success')
        return redirect(url_for('properties.index'))

    return render_template('properties/add.html', form=form)


@properties_bp.route('/<int:property_id>')
@login_required
def details(property_id):
    # On récupère l'immeuble, mais on s'assure qu'il appartient bien au user connecté (Sécurité !)
    property = current_user.properties.filter_by(id=property_id).first_or_404()

    # On récupère les appartements de cet immeuble
    units = property.units.all()

    return render_template('properties/details.html', property=property, units=units)

@properties_bp.route('/<int:property_id>/add_unit', methods=['GET', 'POST'])
@login_required
def add_unit(property_id):
    # Vérification de sécurité (toujours !)
    property = current_user.properties.filter_by(id=property_id).first_or_404()

    if not current_user.can_add_unit():
        flash(f"Limite atteinte pour le plan {current_user.plan_display_name}. Passez à la version supérieure !", "warning")
        return redirect(url_for('main.pricing'))

    form = UnitForm()
    if form.validate_on_submit():
        new_unit = Unit(
            door_number=form.door_number.data,
            rent_amount=form.rent_amount.data,
            property=property # On lie l'appartement à l'immeuble parent
        )
        db.session.add(new_unit)
        db.session.commit()
        flash(f'Appartement "{new_unit.door_number}" ajouté !', 'success')
        return redirect(url_for('properties.details', property_id=property.id))

    return render_template('properties/add_unit.html', form=form, property=property)


@properties_bp.route('/unit/<int:unit_id>/new_tenant', methods=['GET', 'POST'])
@login_required
def new_tenant(unit_id):
    # 1. Récupération de l'appartement
    unit = Unit.query.get_or_404(unit_id)

    # 2. Sécurité : Vérifier que cet appartement appartient bien au user connecté
    if unit.property.owner != current_user:
        flash("Accès interdit.", "danger")
        return redirect(url_for('properties.index'))

    # 3. Règle Métier : Vérifier si l'appart est déjà occupé
    if unit.current_tenant:
        flash(f"Cet appartement est déjà occupé par {unit.current_tenant.full_name}.", "warning")
        return redirect(url_for('properties.details', property_id=unit.property.id))

    form = TenantForm()

    if form.validate_on_submit():
        # Création du locataire
        tenant = Tenant(
            full_name=form.full_name.data,
            phone=form.phone.data,
            email=form.email.data,
            entry_date=form.entry_date.data,
            unit=unit, # Liaison avec l'appartement
            is_active=True
        )
        db.session.add(tenant)
        db.session.commit()

        flash(f'Locataire {tenant.full_name} ajouté avec succès !', 'success')
        # Retour à la vue de l'immeuble
        return redirect(url_for('properties.details', property_id=unit.property.id))

    return render_template('properties/new_tenant.html', form=form, unit=unit)


@properties_bp.route('/tenant/<int:tenant_id>')
@login_required
def tenant_details(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)

    # Sécurité : Vérifier que le locataire est bien dans un immeuble du user
    if tenant.unit.property.owner != current_user:
        flash("Vous n'avez pas accès à ce dossier.", "danger")
        return redirect(url_for('properties.index'))

    # On trie les paiements par date décroissante (le plus récent en haut)
    payments = tenant.payments.order_by(Payment.date_paid.desc()).all()

    return render_template('properties/tenant_details.html', tenant=tenant, payments=payments)


# === EDIT ROUTES ===

@properties_bp.route('/property/<int:property_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_property(property_id):
    """Edit existing property"""
    property = current_user.properties.filter_by(id=property_id).first_or_404()
    
    form = PropertyForm(obj=property)
    
    if form.validate_on_submit():
        property.name = form.name.data
        property.address = form.address.data
        db.session.commit()
        flash(f'Immeuble "{property.name}" modifié avec succès !', 'success')
        return redirect(url_for('properties.details', property_id=property.id))
    
    return render_template('properties/edit_property.html', form=form, property=property)


@properties_bp.route('/unit/<int:unit_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_unit(unit_id):
    """Edit existing unit"""
    unit = Unit.query.get_or_404(unit_id)
    
    # Security check
    if unit.property.owner != current_user:
        flash("Accès interdit.", "danger")
        return redirect(url_for('properties.index'))
    
    form = UnitForm(obj=unit)
    
    if form.validate_on_submit():
        unit.door_number = form.door_number.data
        unit.rent_amount = form.rent_amount.data
        db.session.commit()
        flash(f'Appartement "{unit.door_number}" modifié avec succès !', 'success')
        return redirect(url_for('properties.details', property_id=unit.property.id))
    
    return render_template('properties/edit_unit.html', form=form, unit=unit)


@properties_bp.route('/tenant/<int:tenant_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_tenant(tenant_id):
    """Edit existing tenant"""
    tenant = Tenant.query.get_or_404(tenant_id)
    
    # Security check
    if tenant.unit.property.owner != current_user:
        flash("Accès interdit.", "danger")
        return redirect(url_for('properties.index'))
    
    form = TenantForm(obj=tenant)
    
    if form.validate_on_submit():
        tenant.full_name = form.full_name.data
        tenant.phone = form.phone.data
        tenant.email = form.email.data
        tenant.entry_date = form.entry_date.data
        db.session.commit()
        flash(f'Locataire "{tenant.full_name}" modifié avec succès !', 'success')
        return redirect(url_for('properties.tenant_details', tenant_id=tenant.id))
    
    return render_template('properties/edit_tenant.html', form=form, tenant=tenant)


# DELETE ROUTES

@properties_bp.route('/property/<int:property_id>/delete', methods=['POST'])
@login_required
def delete_property(property_id):
    property = current_user.properties.filter_by(id=property_id).first_or_404()
    
    property_name = property.name
    db.session.delete(property)
    db.session.commit()
    
    flash(f'Immeuble "{property_name}" supprimé avec succès.', 'success')
    return redirect(url_for('properties.index'))


@properties_bp.route('/unit/<int:unit_id>/delete', methods=['POST'])
@login_required
def delete_unit(unit_id):
    unit = Unit.query.get_or_404(unit_id)
    
    # Security check
    if unit.property.owner != current_user:
        flash("Accès interdit.", "danger")
        return redirect(url_for('properties.index'))
    
    property_id = unit.property.id
    unit_number = unit.door_number
    
    db.session.delete(unit)
    db.session.commit()
    
    flash(f'Appartement "{unit_number}" supprimé.', 'success')
    return redirect(url_for('properties.details', property_id=property_id))


@properties_bp.route('/tenant/<int:tenant_id>/delete', methods=['POST'])
@login_required
def delete_tenant(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    
    # Security check
    if tenant.unit.property.owner != current_user:
        flash("Accès interdit.", "danger")
        return redirect(url_for('properties.index'))
    
    property_id = tenant.unit.property.id
    tenant_name = tenant.full_name
    
    db.session.delete(tenant)
    db.session.commit()
    
    flash(f'Locataire "{tenant_name}" supprimé.', 'success')
    return redirect(url_for('properties.details', property_id=property_id))
