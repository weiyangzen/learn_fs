<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/togglesebool.c -->
# sources/security-integrity/selinux/libselinux/utils/togglesebool.c

## Purpose
Toggles one or more SELinux booleans and commits the transaction.

## Important APIs, Types, And Functions
Uses `security_get_boolean_active()`, `security_set_boolean()`, `security_commit_booleans()`, and rollback helper that restores processed booleans to active values.

## Control Flow
Each boolean is flipped in pending state. On any set/read error, previously processed booleans are rolled back and the program exits. Successful commit syslogs each changed boolean with username or uid.

## State And Persistence Behavior
Changes pending booleans and commits them to kernel/policy boolean state. Rollback attempts to restore pending values before commit.

## Dependencies And Integration Points
Integrates boolean APIs, syslog, pwd lookup, and user identity.

## Risks And Test Signals
Risks include rollback best-effort semantics, commit failure after pending changes, races with other boolean changes, and logging accuracy. Tests should cover toggling on/off, unknown boolean, mid-list failure rollback, commit failure, disabled SELinux, and syslog identity.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/togglesebool.c -->
