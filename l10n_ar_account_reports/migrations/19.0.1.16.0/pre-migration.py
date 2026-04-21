import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Pre-migración l10n_ar_account_reports 19.0.1.16.0
    Elimina índices de inflación duplicados para evitar error al cargar
    inflation_adjustment_index.xml que tiene noupdate=1 pero en modo
    upgrade falla si ya existen registros.
    """
    _logger.info("l10n_ar_account_reports pre-migrate: limpiando inflation_adjustment_index")
    cr.execute("DELETE FROM inflation_adjustment_index")
    _logger.info(f"  ✓ {cr.rowcount} índices de inflación eliminados para reinstalación limpia")