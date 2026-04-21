import logging
import re

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Pre-migración account_accountant_ux 19.0.1.0.0
    Elimina campos obsoletos del arch_db de res_config_settings_view_form:
    - use_company_currency_on_followup
    - use_search_filter_amount
    """
    _logger.info("account_accountant_ux pre-migrate: limpiando campos obsoletos de res_config_settings")
    cr.execute("""
        SELECT id FROM ir_ui_view
        WHERE id IN (
            SELECT res_id FROM ir_model_data
            WHERE module = 'account_accountant_ux'
              AND name = 'res_config_settings_view_form'
              AND model = 'ir.ui.view'
        )
        AND (
            arch_db::text LIKE '%use_company_currency_on_followup%'
            OR arch_db::text LIKE '%use_search_filter_amount%'
        )
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
            AND arch_db::text LIKE '%%use_company_currency_on_followup%%'
        """, (view_id,))
        if cr.rowcount > 0:
            _logger.info(f"  ✓ use_company_currency_on_followup eliminado (id {view_id})")

        cr.execute("""
            UPDATE ir_ui_view
            SET arch_db = CAST(
                regexp_replace(
                    arch_db::text,
                    '<setting id=\\"use_search_filter_amount\\".*?</setting>',
                    '',
                    'g'
                ) AS jsonb
            )
            WHERE id = %s
            AND arch_db::text LIKE '%%use_search_filter_amount%%'
        """, (view_id,))
        if cr.rowcount > 0:
            _logger.info(f"  ✓ use_search_filter_amount eliminado (id {view_id})")
    else:
        _logger.info("  - res_config_settings_view_form ya está limpia")
