from flask import Flask, render_template, redirect, Response
from wtforms import IntegerField, SubmitField, StringField, DateField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
import pdfkit


class Base(DeclarativeBase):
    pass
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///khata.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)
app.secret_key = "12345"

class Hisab(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    party_name: Mapped[str] = mapped_column(String, nullable=False)
    due_date: Mapped[float] = mapped_column(String, nullable=False)
    purchase_amount: Mapped[str] = mapped_column(Float(250), nullable=False)
    paid: Mapped[str] = mapped_column(Float(250), nullable=False)
    due_amount: Mapped[str] = mapped_column(Float(250), nullable=False)


    def __repr__(self):
        return f"<Hisab id: {self.id}, party_name: {self.party_name}, due_date: {self.due_date}, purchase_amount: " \
               f"{self.purchase_amount}, paid: {self.paid}, due_amount: {self.due_amount}>"


with app.app_context():
    db.create_all()

class KhataForm(FlaskForm):
    party_name = StringField(label="Party Name", validators=[DataRequired()])
    purchase_amount = IntegerField(label="Purchased", validators=[DataRequired()])
    paid = IntegerField(label="Paid", validators=[DataRequired()])
    due_date = DateField(label="Due Date", validators=[DataRequired()])
    submit = SubmitField(label="ENTER")

@app.route("/")
def home():
    return render_template("home.html",)

@app.route("/khata", methods=["GET", "POST"])
def khata():
    my_form = KhataForm()
    if my_form.validate_on_submit():
        party_name = my_form.party_name.data
        purchase_amount = my_form.purchase_amount.data
        paid = my_form.paid.data
        due_date = my_form.due_date.data
        due_amount = purchase_amount - paid

        with app.app_context():
            new_hisab = Hisab(party_name=party_name, due_date=due_date, purchase_amount=purchase_amount, paid=paid, due_amount=due_amount)
            db.session.add(new_hisab)
            db.session.commit()

        return redirect("khata")
    else:
        print(my_form.errors)
    return render_template("khata.html", form=my_form)

@app.route("/reports")
def show_reports():
    data = Hisab.query.order_by(Hisab.due_date).all()
    return render_template("reports.html", data=data)

@app.route("/download_pdf")
def download_pdf():
    data = Hisab.query.order_by(Hisab.due_date).all()
    rendered_html = render_template("reports.html", data=data)
    path_to_wkhtmltopdf = '/usr/bin/wkhtmltopdf'  # Update this path accordingly

    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)
    options = {
        'enable-local-file-access': None,  # This allows local file access
        'quiet': ''
    }

    pdf = pdfkit.from_string(rendered_html, False, configuration=config, options=options)
    response = Response(pdf, mimetype='application/pdf')
    response.headers['Content-Disposition'] = 'attachment; filename=reports.pdf'
    return response

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
