# sources/test-tools/xfstests-bld/fstests-bld/popt/poptint.h

Purpose: private header shared by popt implementation files. It exposes internal memory helpers, bitmask helpers, argument pointer union, context layout, option-stack state, i18n macros, and internal function declarations.

Important types/macros: `_free`, `pbm_set`, PBM allocation/set/clear/test macros, `poptArg`, `_poptArgMask`, `_poptGroupMask`, `poptArgType`, `poptGroup`, `F_ISSET`, `LF_ISSET`, `CBF_ISSET`, `poptSubstituteHelpI18N`, `struct optionStackEntry`, and `struct poptContext_s`.

Control flow/state: `optionStackEntry` is the parser frame used for original argv, aliases, and stuffed args. `poptContext_s` stores parser stack, leftovers, option table, aliases/execs, final argv, maincall, deferred exec, exec search path, help text, and stripped-argument bitmap. Macros drive flag decoding throughout `popt.c` and `popthelp.c`.

Dependencies/integration: includes `stdint.h`, optional iconv/langinfo/libintl headers, and depends on public types from `popt.h` via `system.h`. It declares `POPT_fprintf`, `POPT_dgettext`, `POPT_prev_char`, and `POPT_next_char` for use across files.

Risks: because this header exposes private structure layout to all implementation files, accidental field changes affect ABI assumptions inside the library. PBM macros assume correctly sized allocations and valid indices. `poptSubstituteHelpI18N` mutates option table pointers as a compatibility hack.

Test signals: parser, help, config, and bitset tests exercise this indirectly; structural issues usually show as parse failures, memory leaks, or crashes.
