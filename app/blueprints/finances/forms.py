from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime

class PaymentForm(FlaskForm):
    amount = FloatField('Montant Reçu (CFA)', validators=[DataRequired()])

    # Génération automatique des 12 derniers mois pour la liste déroulante
    period = SelectField('Période concernée', validators=[DataRequired()], choices=[])

    submit = SubmitField('Valider et Générer Quittance')

    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        # On génère une liste dynamique : "2023-11 (Novembre)"
        today = datetime.today()
        months = []
        for i in range(0, 6): # Propose les 6 derniers mois et le mois actuel
             # Logique simplifiée pour l'exemple, à adapter selon besoins
             year = today.year
             month = today.month - i
             if month <= 0:
                 month += 12
                 year -= 1
             key = f"{year}-{month:02d}"
             label = f"{key}" # On pourrait mettre les noms des mois en français ici
             months.append((key, label))
        self.period.choices = months
