from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SECRET_KEY'] = '23a701802563066f3d81d512'  # Keep secret in env for prod
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable tracking for performance

#configuration setup for mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] =   '****'# your Gmail address
app.config['MAIL_PASSWORD'] = '***'#'your_16_digit_app_password'  # the App Password you just generated
app.config['MAIL_DEFAULT_SENDER'] = '****'#sender email address

# Extensions initialization
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login_page"  # Name of your login route function
login_manager.login_message_category = "info"

mail = Mail(app)

migrate = Migrate(app, db)

# Import routes after app and extensions initialized to avoid circular imports
from market import routes
