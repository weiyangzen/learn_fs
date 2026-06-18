# sources/security-integrity/fscrypt/security/privileges.go

## Purpose
`privileges.go` manages process credentials for fscrypt, especially PAM and keyring flows that need to temporarily act as a target user or regain root.

## Important APIs, Types, and Functions
`Privileges` stores effective UID, effective GID, and supplementary groups. Public functions are `ProcessPrivileges`, `UserPrivileges`, `SetProcessPrivileges`, `SetUids`, and `GetUids`.

## Control Flow
`ProcessPrivileges` reads current uid/gid and supplementary groups. `UserPrivileges` converts an `os/user.User` to target UID/GID/groups. `SetProcessPrivileges` elevates effective UID to root, sets groups, effective GID, then effective UID, and logs resulting privileges. `SetUids` first sets all real/effective/saved UIDs to root, then sets requested real/effective/saved IDs. `GetUids` reads real/effective/saved IDs.

## State and Persistence
These functions mutate process-wide credentials through libc calls. No disk state is written. Saved `Privileges` objects are in-memory snapshots used to restore previous credentials.

## Dependencies and Integration Points
Uses cgo libc functions rather than raw syscalls because Go raw credential syscalls are per-thread on Linux. This is critical for `pam_fscrypt`, PAM handle privilege switching, and keyring v2 user-claim operations.

## Risks
Privilege changes are security-critical. Incorrect ordering or failure to restore can leave the process with wrong privileges. The code assumes root capability for many transitions. Because these are process-wide, concurrent goroutines may observe changed privileges.

## Test Signals
`security_test.go` is only a trivial stub. Indirect tests exercise privilege functions through keyring and PAM integration when run with root.
