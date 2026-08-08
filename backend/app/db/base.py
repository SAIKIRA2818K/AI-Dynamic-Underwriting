# Import all the models, so that Base has them before being
# imported by Alembic or used for creating tables.
from app.db.session import Base
# from app.models.user import User  # Example placeholder for future models
# from app.models.loan_application import LoanApplication  # Example placeholder
