<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/run_init/run_init.c -->
# sources/security-integrity/selinux/policycoreutils/run_init/run_init.c

## Purpose
Authenticates the caller and runs an init script or command under the SELinux context stored in the configured `initrc_context` file.

## Important APIs, Types, And Functions
Key functions are `authenticate_via_pam()` or `authenticate_via_shadow_passwd()`, `authenticate_user()`, `get_init_context()`, and `main()`. It uses libselinux (`is_selinux_enabled`, `selinux_contexts_path`, `setexeccon`), PAM or shadow/crypt, optional audit login uid lookup, passwd lookup, and `execvp`.

## Control Flow
`main()` initializes localization, requires SELinux, validates that a command is present, authenticates the login uid or real uid, reads the first nonblank context line from `$(selinux_contexts_path())/initrc_context`, changes directory to `/`, sets the exec context, and then either execs the requested command directly or execs `/usr/sbin/open_init_pty` with the original argument vector if that helper is executable.

## State And Persistence
It does not persist configuration itself, but consumes SELinux context configuration and can cause the child process to run with a new exec context. PAM may update authentication/accounting state; the child process may mutate system state as an init command.

## Dependencies And Integration Points
This utility bridges user authentication, SELinux policy contexts, and init/service scripts. It integrates with the optional `open_init_pty` helper to ensure PTY labels align with the initrc domain.

## Risks And Edge Cases
If `initrc_context` is missing or empty, execution fails. The shadow authentication path zeroes only the plaintext password and exits on several auth errors. Direct exec without `open_init_pty` may occur if the helper is not installed or executable.

## Test Signals
Exercise PAM and shadow builds, missing command, missing/empty context file, failed authentication, `setexeccon` failure, helper-present versus helper-absent execution, and child exit behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/run_init/run_init.c -->
