from app import app, db
from app.models import Bug, Device, Experience, Tester

# Add context to the flask shell
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Bug':Bug, 'Device':Device, 'Experience':Experience, 'Tester':Tester}