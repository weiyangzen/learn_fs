# sources/test-tools/xfstests-bld/fstests-bld/popt/popt.c

Purpose: core implementation of the popt option parser. It creates and owns `poptContext`, walks option tables, handles long/short options, alias expansion, exec expansion, leftover arguments, stripped arguments, callbacks, typed argument storage, and experimental Bloom-filter style `poptBits`.

Important APIs/functions: `poptGetContext`, `poptResetContext`, `poptGetNextOpt`, `poptGetOptArg`, `poptGetArg`, `poptPeekArg`, `poptGetArgs`, `poptFreeContext`, `poptAddAlias`, `poptAddItem`, `poptBadOption`, `poptStrerror`, `poptStuffArgs`, `poptStrippedArgv`, numeric save helpers, string/argv/bitset helpers, and `poptSetExecPath`. Private helpers include callback walkers, `handleAlias`, `handleExec`, `findOption`, `expandNextArg`, and `execCommand`.

Control flow: callers allocate a context with the original argv and option table, then repeatedly call `poptGetNextOpt`. The parser pops exhausted alias/stuffed frames, identifies leftovers and `--`, parses long options including `--opt=arg`, falls back to short-option clusters, expands aliases by pushing a new `optionStackEntry`, records an exec item for post-parse `execvp`, locates table entries recursively, fetches required/optional arguments, saves typed values, invokes callbacks, and returns option `val` when appropriate. End of input triggers POST callbacks, optional `maincall`, or an exec command.

State/persistence: `poptContext_s` persists argv stack frames, leftovers, aliases, execs, final argv, app name, exec path, optional help text, and strip bitmaps until reset/free. Alias/stuffed argv are duplicated into heap storage; `finalArgv` is rebuilt across parsing. `poptBits` uses global tunables `_poptBitsN/M/K` and hashes from `poptJlu32lpair`. Random numeric options use a static seed.

Dependencies/integration: depends on `system.h`, `poptint.h`, libc allocation/string/process APIs, `execvp`, `PATH`, `POSIXLY_CORRECT`/`POSIX_ME_HARDER`, and option/config records created by `poptconfig.c`. Help output and tests consume the public API declared in `popt.h`.

Risks: many allocation failures are commented as impossible; several realloc assignments overwrite original pointers. `execCommand` deliberately executes configured commands after dropping privileges when possible, so config-file trust matters. Type punning and alignment checks are architecture-sensitive. `poptBitsDel` clears Bloom-filter bits and can create false negatives. Alias recursion is bounded by `POPT_OPTION_DEPTH`, but complex alias/argument substitution still has subtle side effects.

Test signals: `test1.c` and `testit.sh` exercise option parsing, aliases, execs, optional arguments, callbacks, POSIX mode, numeric conversions, bit operations, `POPT_ARG_ARGV`, `POPT_ARG_BITSET`, help/usage, and leftovers. `tdict.c` exercises `poptBits`.
