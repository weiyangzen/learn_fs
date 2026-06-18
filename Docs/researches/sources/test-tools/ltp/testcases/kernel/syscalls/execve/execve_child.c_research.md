# sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve_child.c

Purpose: Shared helper for `execve02`, `execve04`, and `execve05`, distinguishing expected successful and forbidden exec paths.

Important APIs/types/functions: `TST_NO_DEFAULT_MAIN`, `tst_reinit()`, `strcmp()`, `tst_res()`, and return code 0.

Control flow: If invoked with `argv[1] == "canary"`, it reports pass for the concurrent execve05 case. Otherwise it reports failure because execve02/04 are expected not to execute it.

State and persistence behavior: No durable state; its behavior is entirely driven by argv.

Dependencies and integration points: Used as a resource file by multiple execve tests, so it encodes both positive and negative sentinel roles.

Risks and test signals: Misusing this helper in a new test without the canary would report failure by design. It is a guard against forbidden exec success.
