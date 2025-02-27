from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

from pages.trade import trade_bp  # Import the trade Blueprint
from pages.aid import aid_bp
from pages.exchangeRates import exchangeRates_bp
from pages.tourism import tourism_bp
from pages.carbondioxide import carbondioxide_bp
from pages.threatenedSpecies import threatenedSpecies_bp
from pages.internet import internet_bp
from pages.health import health_bp
from pages.charts import charts_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong, secure key!

# LoginManager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to the login page if not authenticated

# Mock user database
users = {
    "admin": {"password": "password123"},
    "user1": {"password": "mypassword"}
}

# User model
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Load user function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

# Register the Blueprints
app.register_blueprint(trade_bp)
app.register_blueprint(aid_bp)
app.register_blueprint(exchangeRates_bp)
app.register_blueprint(tourism_bp)
app.register_blueprint(carbondioxide_bp)
app.register_blueprint(threatenedSpecies_bp)
app.register_blueprint(internet_bp)
app.register_blueprint(health_bp)
app.register_blueprint(charts_bp)

@app.route('/')
@login_required  # Require login to access the main page
def main_page():
    return render_template('main.html', user=current_user.id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('main_page'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
