from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FloatField, DateField
from wtforms.validators import DataRequired, Length, Email

class PropertyForm(FlaskForm):
    name = StringField('Nom de l\'immeuble', validators=[
        DataRequired(),
        Length(min=2, max=100, message="Le nom doit faire entre 2 et 100 caractères")
    ])
    address = TextAreaField('Adresse complète', validators=[
        Length(max=200, message="L'adresse est trop longue")
    ])
    submit = SubmitField('Enregistrer l\'immeuble')

class UnitForm(FlaskForm):
    door_number = StringField('Numéro de Porte / Identifiant', validators=[
        DataRequired(),
        Length(max=20, message="Ex: A1, 2ème Gauche...")
    ])
    rent_amount = FloatField('Montant du Loyer (CFA)', validators=[
        DataRequired(message="Le montant est obligatoire")
    ])
    submit = SubmitField('Ajouter l\'appartement')


class TenantForm(FlaskForm):
    full_name = StringField('Nom complet (Prénom + Nom)', validators=[
        DataRequired(),
        Length(min=3, max=100)
    ])
    phone = StringField('Téléphone (WhatsApp)', validators=[
        DataRequired(),
        Length(min=9, max=20, message="Format ex: 77 000 00 00")
    ])
    email = StringField('Email (Optionnel)', validators=[
        Email(message="Email invalide"),
        Length(max=120)
    ])
    entry_date = DateField("Date d'entrée", format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Valider le Locataire')
