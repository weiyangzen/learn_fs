# sources/sync-backup/rsync/popt/popt.h

Purpose: Public API header for the bundled popt option parser. It defines option table syntax, argument type constants, flag bits, error codes, context flags, alias/exec item records, callback contracts, and exported parser/config/help functions used by popt consumers.

Important APIs, types, and functions: `struct poptOption` is the core option descriptor with long/short names, `argInfo`, storage pointer, return value, help text, and argument description. `struct poptAlias`, `poptItem`, `poptContext`, `poptCallbackType`, and `enum poptCallbackReason` define alias/exec and callback contracts. Public functions include `poptGetContext()`, `poptGetNextOpt()`, `poptGetOptArg()`, `poptReadConfigFiles()`, `poptPrintHelp()`, `poptPrintUsage()`, `poptSaveInt()` and related typed save helpers, plus experimental `poptBits*()` helpers.

Control flow and state: This header is declarative, but it encodes parser behavior through bit masks. `POPT_ARG_*` selects conversion/storage behavior, `POPT_ARGFLAG_*` modifies parsing and help output, callback flags drive pre/post/option callback invocation, and `POPT_CONTEXT_*` controls argv treatment. `POPT_AUTOHELP`, `POPT_AUTOALIAS`, and `POPT_TABLEEND` are table construction macros that integrate with `popthelp.c`.

State and persistence behavior: The opaque `poptContext` owns argv copies, aliases, exec entries, leftover args, final argv, and help text in `poptint.h`. Config reading APIs persist aliases and exec items into the context. Callers own context lifetime via `poptFreeContext()`/`poptFini()`, while some returned strings/argv arrays are malloc-backed.

Dependencies and integration points: Included by popt implementation files and consumers. It depends only on `stdio.h` publicly, but its declarations tie into `poptconfig.c`, `poptparse.c`, `popthelp.c`, and internal context definitions in `poptint.h`. In rsync, this bundled library supports command-line/config parsing.

Risks and test signals: ABI stability is important because flags and struct layouts are public. Risk areas include ambiguous flag combinations, callback type safety via `void *`, ownership of allocated argv data, and experimental bitset APIs. Good tests cover option conversion, optional args, aliases, config files, help output, and error-code reporting.
