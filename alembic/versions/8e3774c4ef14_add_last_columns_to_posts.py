"""add last columns to posts

Revision ID: 8e3774c4ef14
Revises: e9e26b027d9d
Create Date: 2026-09-06 16:36:22.267215

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e3774c4ef14'
down_revision: Union[str, Sequence[str], None] = 'e9e26b027d9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('published', sa.Boolean(), nullable = False, server_default = 'TRUE'), )
    op.add_column('posts', sa.Column('created_at', sa.TIMESTAMP(timezone= True), nullable = False, server_default = sa.text('NOW()')),)
    pass


def downgrade() -> None:
    op.drop_column('posts', 'published')
    op.drop_column('posts', 'created_at')
    pass
