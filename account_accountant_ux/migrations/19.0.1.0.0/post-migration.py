import logging
import re

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Post-migración account_accountant_ux 19.0.1.0.0
    Elimina campos obsoletos del arch_db DESPUÉS de que el módulo cargue.
    """
    _logger.info("account_accountant_ux post-migrate: limpiando campos obsoletos")
    cr.execute("""
        SELECT id FROM ir_ui_view
        WHERE id IN (
            SELECT res_id FROM ir_model_data
            WHERE module = 'account_accountant_ux'
              AND name = 'res_config_settings_view_form'
              AND model = 'ir.ui.view'
        )
        AND arch_db::text LIKE '%use_company_currency_on_followup%'
    """)
    row = cr.fetchone()
    if row:
        view_id = row[0]
        cr.execute("""
            UPDATE ir_ui_view
            SET arch_db = CAST(
                regexp_replace(
                    regexp_replace(
                        arch_db::text,
                        '<setting id=\\"company_currency_on_follow_up\\"[^<]*(<[^/][^>]*>[^<]*</[^>]*>|<[^/][^>]*/?>)*[^<]*</setting>',
                        '',
                        'g'
                    ),
                    '<block name=\\"main_currency_setting_container\\" position=\\"inside\\">\\s*</block>',
                    '',
                    'g'
                ) AS jsonb
            )
            WHERE id = %s
        """, (view_id,))
        _logger.info(f"  ✓ use_company_currency_on_followup eliminado en post-migrate (id {view_id})")
    else:
        _logger.info("  - res_config_settings_view_form ya está limpia")

    # Reactivar la vista después de limpiar el campo obsoleto
    # (fue desactivada en el pre-migrate de account_payment_pro)
    cr.execute("""
        UPDATE ir_ui_view SET active = True
        WHERE id IN (
            SELECT res_id FROM ir_model_data
            WHERE module = 'account_accountant_ux'
              AND name = 'res_config_settings_view_form'
              AND model = 'ir.ui.view'
        )
        AND active = False
    """)
    if cr.rowcount > 0:
        _logger.info("  ✓ account_accountant_ux.res_config_settings_view_form reactivada")