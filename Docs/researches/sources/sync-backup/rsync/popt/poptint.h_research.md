# sources/sync-backup/rsync/popt/poptint.h

Purpose: Internal popt header that exposes parser context layout, option stack state, internal macros, union casts for option storage, bitmap helpers, and localization wrappers to the implementation files.

Important APIs, types, and functions: `_free()` safely frees possibly const pointers and returns NULL. `pbm_set` and `PBM_*` macros manage parse-position bitmaps. `poptArg` is a union for type-specific access to `opt->arg`. `struct optionStackEntry` stores active argv stack frames, next argument state, current alias, and stuffed-argument markers. `struct poptContext_s` stores option stack, leftovers, options, aliases, execs, final argv, maincall, exec path, help text, and stripped-arg bitmap.

Control flow: Macros `poptArgType()`, `poptGroup()`, `F_ISSET()`, `LF_ISSET()`, and `CBF_ISSET()` centralize flag decoding. `poptSubstituteHelpI18N()` swaps built-in help tables for translated variants. The header also declares `POPT_fprintf()`, `POPT_prev_char()`, and `POPT_next_char()`, plus translation macros `D_`, `POPT_`, and `N_`.

State and persistence behavior: Defines all mutable context state used by parser, config, and help modules. Context fields persist across parse calls until reset/free, while bitmaps track consumed/stripped args.

Dependencies and integration points: Includes `stdint.h`, depends on public `popt.h`, and is included by the implementation files. It bridges public ABI-compatible types to private implementation details.

Risks and test signals: Since it exposes private struct layout across bundled source files, layout changes must be synchronized. Risks include bitmap allocation sizing, macro side effects, flag mask drift with `popt.h`, and translation macro build matrix issues. Tests should compile all feature combinations and exercise alias stacking, stripped argv, leftovers, and translated help.
