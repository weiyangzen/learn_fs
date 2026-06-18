# sources/security-integrity/audit-userspace/src/auditd-sendmail.c

## Purpose
`auditd-sendmail.c` sends email alerts for audit daemon disk-space actions. It wraps `/usr/lib/sendmail` execution and writes a simple message to the child's stdin.

## Important APIs, Types, And Functions
Public API is `sendmail(subject, content, mail_acct)`. Internal helper `safe_popen` creates a pipe, forks, redirects child stdin, builds `sendmail -t -f<acct>`, and execs the configured `email_command`.

## Control Flow
`sendmail` checks that `email_command` is executable, calls `safe_popen`, converts the returned write fd to a `FILE *`, writes To/From/Subject headers plus content and SMTP terminator, then closes the stream. On `fdopen` failure it kills the child and logs an error.

## State And Persistence
No local persistent state exists. It reads global `email_command` from `auditd-config.c`. It creates a child process and writes email content over a pipe; actual delivery persistence is delegated to the mailer.

## Dependencies And Integration
It depends on libc process/pipe APIs, signals, `libaudit`, `private.h`, and `auditd-config.h`. It is called from `auditd-event.c` for `FA_EMAIL` disk space warnings.

## Risks
The sender account is included in `-f%s`; parser validation limits characters but this helper still trusts the value. The child inherits most file descriptors except stdin adjustment because it does not close descriptors broadly. The parent does not wait here, relying on daemon SIGCHLD handling. Delivery failures after `fclose` are not inspected.

## Test Signals
`format_event_test` links this file, but no mail-specific tests exist. Useful tests would override `email_command`, simulate pipe/fork/fdopen failures, validate argv construction, and verify no descriptor leaks in the child path.
