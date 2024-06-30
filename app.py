from flask import Flask, render_template, redirect, url_for, flash, request
from config import Config
from forms import ReservationForm, LoginForm, RegistrationForm
from models import db, Service, Reservation, User
from datetime import datetime, timedelta
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import os


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    if Service.query.count() == 0:
        services = [
            {'name': 'Czyszczenie tapicerki', 'price': 200.0, 'description': 'Profesjonalne czyszczenie tapicerki samochodowej, usuwa plamy i odświeża wnętrze Twojego auta.'},
            {'name': 'Mycie zewnętrzne', 'price': 100.0, 'description': 'Dokładne mycie zewnętrzne, które sprawi, że Twój samochód będzie wyglądał jak nowy.'},
            {'name': 'Polerowanie lakieru', 'price': 300.0, 'description': 'Specjalistyczne polerowanie lakieru, które przywraca blask i głębię koloru.'},
            {'name': 'Regeneracja reflektorów', 'price': 150.0, 'description': 'Profesjonalna regeneracja reflektorów, która przywraca ich przejrzystość i jasność, poprawiając wygląd samochodu i bezpieczeństwo jazdy.'},
            {'name': 'Detailing wnętrza', 'price': 250.0, 'description': 'Kompleksowe czyszczenie wnętrza pojazdu, które usuwa kurz, brud i nieprzyjemne zapachy.'},
            {'name': 'Czyszczenie silnika', 'price': 180.0, 'description': 'Profesjonalne czyszczenie komory silnika, które poprawia wygląd i działanie silnika.'},
            {'name': 'Odświeżanie klimatyzacji', 'price': 120.0, 'description': 'Czyszczenie i odgrzybianie systemu klimatyzacji, które zapewnia świeże i zdrowe powietrze wewnątrz pojazdu.'}
        ]
        for service in services:
            new_service = Service(name=service['name'], price=service['price'], description=service['description'])
            db.session.add(new_service)
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not check_password_hash(user.password_hash, form.password.data):
            flash('Niepoprawna nazwa użytkownika lub hasło')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        flash('Pomyślnie zalogowano!')
        return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('Pomyślnie wylogowano!')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password_hash=generate_password_hash(form.password.data))
        db.session.add(user)
        db.session.commit()
        flash('Gratulacje, jesteś teraz zarejestrowanym użytkownikiem!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/reservation', methods=['GET', 'POST'])
@login_required
def reservation():
    form = ReservationForm()
    form.service.choices = [(service.id, f"{service.name} - {service.price} zł") for service in Service.query.all()]
    if form.validate_on_submit():
        start_time = datetime.combine(form.date.data, datetime.strptime(form.time.data, "%H:%M").time())
        end_time = start_time + timedelta(hours=1)
        overlapping_reservations = Reservation.query.filter(
            Reservation.start_time < end_time,
            Reservation.end_time > start_time
        ).count()
        if overlapping_reservations == 0:
            new_reservation = Reservation(
                name=form.name.data,
                phone=form.phone.data,
                service_id=form.service.data,
                start_time=start_time,
                end_time=end_time,
                user_id=current_user.id
            )
            db.session.add(new_reservation)
            db.session.commit()
            flash(f"Rezerwacja dla {form.name.data} na usługę {form.service.data} została pomyślnie wykonana.")
            return redirect(url_for('confirmation'))
        else:
            flash('Wybrany termin jest już zajęty. Proszę wybrać inny termin.', 'error')
    return render_template('reservation.html', form=form)

@app.route('/confirmation')
@login_required
def confirmation():
    return render_template('confirmation.html')

@app.route('/oferta')
def oferta():
    services = Service.query.all()
    return render_template('oferta.html', services=services)

@app.route('/dashboard')
@login_required
def dashboard():
    reservations = Reservation.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', reservations=reservations)

@app.route('/cancel/<int:reservation_id>')
@login_required
def cancel_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != current_user.id:
        flash('Nie możesz anulować tej rezerwacji.')
        return redirect(url_for('dashboard'))
    db.session.delete(reservation)
    db.session.commit()
    flash('Twoja rezerwacja została anulowana.')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
