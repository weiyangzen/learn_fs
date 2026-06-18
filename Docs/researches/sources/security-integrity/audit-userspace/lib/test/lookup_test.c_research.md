# sources/security-integrity/audit-userspace/lib/test/lookup_test.c

Purpose: regression test for libaudit lookup tables and audit logging encoding helpers. It includes table headers directly with `_S` redefined into arrays and verifies numeric-to-string and string-to-numeric conversion paths.

Important APIs/functions: helpers `gen_id`, `TEST_I2S`, `TEST_S2I`, per-table tests for architecture syscall tables, action/error/field/flag/fstype/ftype/machine/message/operator tables, optional io_uring and optional ARM/AArch64/RISC-V tests, `test_audit_logging_encoding`, and `main`.

Control flow: `main` seeds `rand(3)`, runs feature-gated table tests, then encoding tests. Each table test validates every known entry and probes random unknown strings/integers for expected failure values.

State and persistence: no persistent state. Uses deterministic pseudo-random generation to avoid accidental known identifiers in negative tests.

Dependencies and integration: includes `libaudit.h` and many `../*_table.h` files. Built and run by `lib/test/Makefile.am`.

Risks and test signals: random negative tests can theoretically collide, but fixed seed and short iteration count make behavior stable. Several reverse lookup exceptions are explicitly excluded for aliases such as `madvise1`, `EWOULDBLOCK`, `EDEADLOCK`, `loginuid`, and machine aliases.
