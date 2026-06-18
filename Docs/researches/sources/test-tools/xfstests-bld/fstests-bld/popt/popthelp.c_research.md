# sources/test-tools/xfstests-bld/fstests-bld/popt/popthelp.c

Purpose: implements automatic help and usage output for popt option tables, including built-in `--help`/`--usage`, nested tables, aliases/execs, default values, i18n domains, wrapping, terminal-width detection, and multibyte display width.

Important APIs/functions: exported globals `poptAliasOptions`, `poptHelpOptions`, `poptHelpOptionsI18N`, and functions `poptPrintHelp`, `poptPrintUsage`, `poptSetOtherOptionHelp`. Private helpers include `displayArgs`, `maxColumnWidth`, `stringDisplayWidth`, `getTableTranslationDomain`, `getArgDescrip`, `singleOptionDefaultValue`, `singleOptionHelp`, `singleTableHelp`, `singleOptionUsage`, `singleTableUsage`, `showShortOptions`, and alias/exec item printers.

Control flow: applications include `POPT_AUTOHELP` in option tables. When help/usage options are parsed, `displayArgs` prints and exits. `poptPrintHelp` emits a usage intro, optional other-help text, computes left-column width, then recursively prints visible options and included tables. `poptPrintUsage` emits a compact one-line/multi-line synopsis with deduplication of included tables and appended alias/exec usage.

State/persistence: reads context state such as `con->options`, aliases, execs, flags, argv0, and `otherHelp`; writes only to `FILE *`. It allocates temporary column/dedup/default strings and frees them.

Dependencies/integration: uses `system.h`, `poptint.h`, gettext macros, `POPT_fprintf`, terminal `TIOCGWINSZ`, `mbsrtowcs`, and parser-internal context fields. Help tables are part of the public API via `popt.h`.

Risks: help formatting is sensitive to terminal width, locale, multibyte conversion, and exact option-table layout. `displayArgs` exits the process, so embedding applications need to expect that behavior. Some buffer sizing relies on estimates; default string truncation and wide-character display padding need regression tests.

Test signals: `testit.sh` contains exact expected `--usage` and `--help` output for `test1`, covering wrapping, defaults, hidden options, aliases/execs, included tables, and callback headings.
