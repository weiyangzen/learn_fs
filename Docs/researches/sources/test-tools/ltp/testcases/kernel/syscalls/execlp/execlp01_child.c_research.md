# sources/test-tools/ltp/testcases/kernel/syscalls/execlp/execlp01_child.c

Purpose: Helper executable for the `execlp` wrapper test. It is intentionally tiny so success means the parent really replaced the child image with this program.

Important APIs/types/functions: `TST_NO_DEFAULT_MAIN`, `tst_reinit()`, `strcmp()`, `tst_brk()`, and `tst_res()` from the LTP harness.

Control flow: `main()` reinitializes LTP state after exec, validates `argc == 2` and `argv[1] == "canary"`, emits `TPASS`, and returns 0.

State and persistence behavior: No durable state is created; the process image and inherited environment/arguments are the state under test.

Dependencies and integration points: Consumed by the neighboring parent test through `$PATH` lookup or an absolute path discovered with `tst_get_path()`.

Risks and test signals: The helper is a sentinel: any argument/environment mismatch, missing harness reinit, or unexpected execution path produces `TFAIL`; parent-side exec failure is reported before this helper runs.
