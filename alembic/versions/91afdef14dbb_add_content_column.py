"""add content column

Revision ID: 91afdef14dbb
Revises: c7ed4c600626
Create Date: 2026-09-06 16:13:10.927603

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91afdef14dbb'
down_revision: Union[str, Sequence[str], None] = 'c7ed4c600626'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('posts', sa.Column('content', sa.String(), nullable = False))
    pass


def downgrade():
    op.drop_column('posts', 'content')
    pass
