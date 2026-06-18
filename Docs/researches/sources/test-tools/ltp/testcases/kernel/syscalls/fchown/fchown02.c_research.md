# sources/test-tools/ltp/testcases/kernel/syscalls/fchown/fchown02.c

Purpose: verifies superuser `fchown(2)` side effects on setuid/setgid bits: executable files lose both bits, while setgid on a non-group-executable file is preserved.

Important APIs/types/functions: `FCHOWN`, `SAFE_CHMOD`, `SAFE_STAT`, `SAFE_OPEN`, `UID16_CHECK`, `GID16_CHECK`, and mode constants `NEW_PERMS1`, `NEW_PERMS2`, `EXP_PERMS`.

Control flow: setup opens two files. Each test case chmods the file to a special-bit mode, calls `FCHOWN` to current root uid/gid, stats the path, and checks both ownership and resulting mode against the expected clearing/preservation rule.

State/persistence behavior: mutates two files' modes and ownership while root. File descriptors remain open.

Dependencies/integration: requires root and tempdir, plus uid/gid compatibility checks.

Risks/test signals: kernel special-bit clearing semantics are the core. Failures are wrong owner/group or wrong mode after `fchown`.
