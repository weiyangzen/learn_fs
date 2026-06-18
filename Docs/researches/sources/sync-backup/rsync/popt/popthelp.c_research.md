# sources/sync-backup/rsync/popt/popthelp.c

Purpose: Generates popt `--help` and `--usage` output and defines the built-in help/usage option table. It formats option names, argument descriptions, translated help text, alias/exec entries, and terminal-width-aware wrapping.

Important APIs, types, and functions: Exported symbols are `poptAliasOptions`, `poptHelpOptions`, `poptHelpOptionsI18N`, `poptPrintHelp()`, `poptPrintUsage()`, and `poptSetOtherOptionHelp()`. Internal helpers include `displayArgs()`, `maxColumnWidth()`, `stringDisplayWidth()`, `getTableTranslationDomain()`, `getArgDescrip()`, `singleOptionDefaultValue()`, `singleOptionHelp()`, `maxArgWidth()`, `singleTableHelp()`, `singleOptionUsage()`, `singleTableUsage()`, and `showShortOptions()`.

Control flow: `displayArgs()` is registered as a callback and exits after printing help or usage. `poptPrintHelp()` prints a usage intro, optional custom help tail, computes column widths, and recursively traverses included option tables and alias/exec tables. `poptPrintUsage()` builds a compact one-line form, tracks already-seen option tables to avoid recursion duplicates, emits grouped short options, then walks tables and context items.

State and persistence behavior: `poptSetOtherOptionHelp()` replaces `con->otherHelp`. Help generation reads context state but does not mutate parser progress. Static `poptHelpOptionsI18N` points at an i18n-aware table. Formatting uses heap buffers for wrapped text and default-value strings.

Dependencies and integration points: Depends on `system.h`, `poptint.h`, optional terminal `ioctl(TIOCGWINSZ)`, optional multibyte support via `mbsrtowcs`, and translation macros from `poptint.h`. It integrates with the public `POPT_AUTOHELP` and `POPT_AUTOALIAS` macros from `popt.h`.

Risks and test signals: Risks include formatting regressions, multibyte width miscalculation, recursive include-table loops, hidden option leakage, and default-value display reading mis-typed `opt->arg` pointers. Tests should compare help/usage output for long/short/toggle/options, included tables, aliases, terminal width changes, i18n domains, and custom `otherHelp`.
