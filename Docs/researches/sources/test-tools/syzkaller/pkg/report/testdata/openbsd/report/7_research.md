# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/7

Purpose: Negative OpenBSD fixture combining relinking failure, login prompts, and normal syzkaller startup logs. It has no expected title.

Important parser APIs and patterns: like report/5, this protects crash detection from `reorder_kernel` text. It also includes benign fuzzer log lines (`fuzzer started`, manager dial, unsupported features) that should not affect OpenBSD report parsing.

Control flow: the console shows `reorder_kernel: kernel relinking fail`, OpenBSD login banners, an accidental `trace` at login with password failure, SSH host-key warning, and syzkaller startup messages. There is no kernel panic, DDB crash prompt, `Stopped at`, or stack.

State and persistence: static no-crash fixture representing VM boot/connection noise and fuzzer initialization state.

Dependencies and integration: integrated with `ContainsCrash` negative tests for OpenBSD. It ensures infrastructure output and syzkaller logs are ignored by kernel crash parsing.

Risks: a loose match on `trace`, `kernel`, or `relinking fail` could produce false positives, blocking fuzzing with bogus crashes.

Test signals: expected behavior is no report.
