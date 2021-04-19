"""empty message

Revision ID: 28ff2e520784
Revises: 
Create Date: 2021-04-11 16:54:26.765426

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '28ff2e520784'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('shopping_cart',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('CREATED', 'CANCELED', 'FINISHED', name='status'), nullable=False),
    sa.Column('isPriority', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('shopping_cart')
    # ### end Alembic commands ###