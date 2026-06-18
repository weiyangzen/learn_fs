<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/reject_unknown.c -->
# sources/security-integrity/selinux/libselinux/src/reject_unknown.c

## Purpose
Reads whether the kernel rejects policy queries involving unknown classes or permissions.

## Important APIs, Types, And Functions
`security_reject_unknown()` reads `<selinux_mnt>/reject_unknown` and parses an integer.

## Control Flow
The function validates `selinux_mnt`, opens the control file, reads a small buffer, parses with `sscanf()`, and returns the parsed value.

## State And Persistence Behavior
Read-only selinuxfs access; no local caching or persistence.

## Dependencies And Integration Points
Used by `selinux_set_mapping()` to decide whether unknown mapping entries are fatal.

## Risks And Test Signals
Tests should cover missing mount, missing/unreadable control file, malformed content, and kernel values `0`/`1`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/reject_unknown.c -->
