## sources/security-integrity/attr/include/nls.h

Purpose: gettext compatibility wrapper.

It includes locale support, maps `_()` to `gettext` when NLS is enabled, and provides no-op `textdomain`/`bindtextdomain` otherwise. State is process locale/textdomain. Dependencies are `ENABLE_NLS` and libintl. Risks are global locale effects and macro substitution in all tools. Test signals are translated and `LC_MESSAGES=C` test runs.
