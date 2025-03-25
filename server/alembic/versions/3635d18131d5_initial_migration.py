"""Initial migration

Revision ID: 3635d18131d5
Revises: 029810bf17c0
Create Date: 2025-03-25 08:32:41.961691

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3635d18131d5'
down_revision: Union[str, None] = '029810bf17c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task_input', sa.Column('type', sa.String(), server_default='string', nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('task_input', 'type')
    # ### end Alembic commands ###
