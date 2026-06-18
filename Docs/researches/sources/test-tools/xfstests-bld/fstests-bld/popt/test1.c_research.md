# sources/test-tools/xfstests-bld/fstests-bld/popt/test1.c

Purpose: comprehensive popt test program used by `testit.sh`. It declares a large option table covering flags, typed arguments, callbacks, included tables, aliases/execs, help, optional args, bit operations, argv accumulation, and bitsets, then prints a normalized summary for comparison.

Important functions/state: `option_callback` prints callback events on the second parse pass; `resetVars` resets all globals and frees accumulated argv/bitset state; `main` reads config/defaults, parses once, resets context and variables, parses again, and prints changed values plus leftovers.

Control flow: the deliberate two-pass parse tests `poptResetContext`. The option table includes callback tables before/after normal options, `POPT_AUTOALIAS`, and `POPT_AUTOHELP`. Main handles errors with `poptBadOption`/`poptStrerror`, then emits deterministic output based on globals modified by parsing.

State/persistence: many globals hold option targets. `aArgv` strings are caller-owned and freed in `resetVars`; `aBits` is cleared but not freed until process exit. The context stores aliases from `test-poptrc` and default config.

Dependencies/integration: depends on the popt library, `test-poptrc`, `$HOME/.popt` behavior via default config, and the shell harness's expected output.

Risks: exact output is sensitive to help wrapping width and program name (`lt-test1` under libtool). Floating comparisons use direct inequality for test reporting. Memory ownership of string options intentionally leaks or is process-lifetime in the library design.

Test signals: `testit.sh` has nearly sixty cases against this program, making it the strongest regression signal for parser behavior.
