# sources/security-integrity/audit-userspace/init.d/augenrules.in

Purpose: Shell utility that concatenates `/etc/audit/rules.d/*.rules` into `/etc/audit/audit.rules`, normalizes special directives, optionally checks for changes, and optionally loads rules with auditctl.

Important variables and functions: `DestinationFile=/etc/audit/audit.rules`, `SourceRulesDir=/etc/audit/rules.d`, `TmpRules=$(mktemp /tmp/aurules.XXXXXXXX)`, `auditctl_bin=@sbindir@/auditctl`, `try_load`, and `check_immutable`.

Control flow: Parses `--check` and `--load`. Verifies source rules directory, creates a restrictive temporary file under `umask 0137`, concatenates version-sorted `.rules` files, strips blank/comment lines, normalizes CR endings, and uses awk to move the last bare `-D` to the first output line, last `-b` second, last `-f` third, and last `-e` last. It compares the temporary rules with destination, exits unchanged when identical, reports change-only mode for `--check`, refuses modifications when audit is immutable (`enabled 2`), backs up existing destination to `.prev`, copies the new file, chmods 0640, restorecons if available, and optionally loads it.

State and persistence: Writes `/etc/audit/audit.rules`, creates `/etc/audit/audit.rules.prev`, and may mutate kernel audit rules through `auditctl -R`.

Dependencies and integration: Generated with substituted auditctl path by configure/make. Used by `audit-rules.service.in` and administrators. Depends on `awk`, `ls -1v`, `grep`, `cmp`, `mktemp`, `restorecon` optionally, and auditctl.

Risks: It iterates `for rules in $(ls ... | grep ...)`, so filenames with whitespace are unsafe. `mktemp` under `/tmp` is mitigated by `mktemp` and restrictive `umask`, but MLS systems require `restorecon` after copy. Immutable mode causes a no-change exit without modifying rules, which is correct but can confuse automation. Rule ordering semantics depend on the awk normalization.

Test signals: Unit tests with multiple `.rules` files covering comments, CRLF, repeated `-D`, `-b`, `-f`, and `-e`; `--check` changed/unchanged behavior; immutable audit state; SELinux label restoration; and `--load` exit status propagation.
