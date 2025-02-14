"""cgnages

Revision ID: adbc8030b62e
Revises: 2b7b844faf5b
Create Date: 2024-12-17 18:37:02.835494

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'adbc8030b62e'
down_revision = '2b7b844faf5b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('services', schema=None) as batch_op:
        batch_op.alter_column('base_price',
               existing_type=sa.FLOAT(),
               type_=sa.Numeric(precision=12, scale=3),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('services', schema=None) as batch_op:
        batch_op.alter_column('base_price',
               existing_type=sa.Numeric(precision=12, scale=3),
               type_=sa.FLOAT(),
               existing_nullable=False)

    # ### end Alembic commands ###
