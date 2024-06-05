from app.models import User, Role
from app import create_app, db
import unittest


another_app = create_app('default')

"""
@another_app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)
"""

@another_app.cli.command('test')
def test():
    """What we run"""
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


