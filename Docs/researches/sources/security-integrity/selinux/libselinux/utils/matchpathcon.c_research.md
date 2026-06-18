<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/matchpathcon.c -->
# sources/security-integrity/selinux/libselinux/utils/matchpathcon.c

## Purpose
CLI for looking up or verifying default SELinux file contexts for paths.

## Important APIs, Types, And Functions
Options include `-V` verify, `-N` raw/no translation, `-n` no header, `-m` forced mode, `-f` file-context file, `-P` policy root, deprecated `-p` subset, and `-q` quiet verify. Uses `selabel_open()`, `selabel_lookup(_raw)()`, and `selinux_file_context_verify()`.

## Control Flow
For each path it strips a trailing slash, lstat()s unless a mode is forced, then either prints expected context or verifies actual context and reports mismatches.

## State And Persistence Behavior
Read-only; only opens a label handle and reads file xattrs during verify.

## Dependencies And Integration Points
Exercises file label backend, policy-root override, raw/translated lookup, and verification compatibility API.

## Risks And Test Signals
Test all mode letters, missing paths, no-match output, verify quiet behavior, raw versus translated output, policy-root override, deprecated subset option, and multiple path error accumulation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/matchpathcon.c -->
