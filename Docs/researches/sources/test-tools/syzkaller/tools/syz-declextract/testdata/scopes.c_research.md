# sources/test-tools/syzkaller/tools/syz-declextract/testdata/scopes.c

Purpose: this fixture stresses switch-scope extraction for syscall arguments, command ranges, helper calls, default cases, large integer constants, and fact propagation.

Important APIs and flow: defines large unsigned/signed macros, `scopes_helper(long cmd, long aux)` with cases for `FOO_IOCTL7`, `FOO_IOCTL8`, and large constants, and `SYSCALL_DEFINE1(scopes0, int x, long cmd, long aux)` that consumes `aux`, switches on `cmd`, handles individual ioctls, grouped cases, macro ranges (`FOO_IOCTL4 ... FOO_IOCTL4 + 2`), numeric ranges (`100 ... 102`), helper calls, and default assignment.

State and persistence: no persistence. Local `tmp` tests return and local-value facts.

Dependencies and integration: includes file operation UAPI constants, syscall macros, and fs helpers. Paired JSON is consumed by declextract tests.

Risks: large constants intentionally overflow signed/unsigned boundaries in ways extractor code must handle deterministically.

Test signals: paired JSON should include syscall metadata, ioctl constants, `foo_ioctl_arg` struct, scopes for individual/range cases, helper call facts, and argument-to-helper flow.
