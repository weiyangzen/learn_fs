<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/newrole/newrole.c -->
# sources/security-integrity/selinux/policycoreutils/newrole/newrole.c

## Purpose
`newrole` is a privileged SELinux RBAC/MLS transition tool analogous to `su`: it authenticates the current login user, validates a requested role/type/level transition, optionally relabels the controlling TTY, and execs the user's shell under the requested SELinux exec context.

## Important APIs, Types, And Functions
Key local helpers are `build_new_range()`, `authenticate_via_pam()` or `authenticate_via_shadow_passwd()`, `extract_pw_data()`, `restore_environment()`, `drop_capabilities()`, `send_audit_message()`, `relabel_tty()`, `restore_tty_label()`, `parse_command_line_arguments()`, and `set_signal_handles()`. It uses libselinux context APIs (`getprevcon`, `context_new`, `context_role_set`, `context_type_set`, `context_range_set`, `security_check_context`, `setexeccon`, `security_compute_relabel`, `fgetfilecon`, `fsetfilecon`), PAM or shadow/crypt authentication, optional libaudit, optional libcap-ng, and a small `hashtab` to map target commands to alternate PAM service names from `/etc/selinux/newrole_pam.conf`.

## Control Flow
`main()` drops unnecessary capabilities, clears the signal mask, initializes NLS, detaches the environment while parsing, requires SELinux, captures the previous context and tty, builds a valid target context from `-r`, `-t`, and `-l`, then authenticates the login uid or real uid. After authentication it relabels the tty, forks, and has the parent wait and restore the tty label. The child reopens stdin/stdout/stderr on the tty, calls `setexeccon(new_context)`, optionally opens a PAM namespace session, writes an audit success record, drops remaining privilege, restores either a scrubbed or preserved environment, and `execv()`s the user's configured shell.

## State And Persistence
Persistent state is limited but security-sensitive: it may relabel the tty device until the parent restores it, opens PAM sessions/namespaces, writes audit records, and runs a shell in the requested context. Environment state is deliberately scrubbed unless `-p` is used. Password buffers are zeroed in the shadow path.

## Dependencies And Integration Points
It integrates with `/etc/passwd`, `/etc/shells`, PAM, `/etc/shadow`, SELinux policy, audit, terminal devices, and package build flags controlling PAM/audit/namespace capability behavior.

## Risks And Edge Cases
The main risks are privilege retention, failure to restore tty labels, partial PAM session cleanup, unsafe preserved environments, MLS level changes from insecure terminals, and command-service parsing in `newrole_pam.conf`. The code mitigates several of these with capability drops, securetty checks, parent cleanup, `O_NONBLOCK` open handling, and context validation.

## Test Signals
Useful tests cover duplicate/invalid role/type/level options, MLS disabled behavior, secure and insecure terminals, PAM and shadow builds, tty label restore on shell exit and exec failure, audit success/failure emission, preserved versus scrubbed environment, and capability-restricted non-root invocation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/newrole/newrole.c -->
