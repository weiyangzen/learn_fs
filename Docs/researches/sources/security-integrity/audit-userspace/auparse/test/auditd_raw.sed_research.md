<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auditd_raw.sed -->
# sources/security-integrity/audit-userspace/auparse/test/auditd_raw.sed

## Purpose
Normalizes raw auditd log text into the same comparison shape as `auparselol_test --check` output for diff testing.

## Important APIs, types, and functions
This is a sed script of substitution commands. It removes or rewrites formatting differences around `cwd`, `comm`, `msg`, hostname, success, exe, terminal, SELinux AVC text, auid/session/login wording, policy/load messages, PAM phrases, and permission strings.

## Control flow
`Makefile.am:diffcheck` pipes `test3.log` through this sed script, sorts the result, and compares it against sorted auparselol parsed output.

## State and persistence behavior
No internal state. It produces transient normalized text for comparison.

## Dependencies and integration points
Depends on sed regex behavior and the exact audit log phrasing emitted by auditd/kernel/libaudit. Integrated only with auparse test targets.

## Risks and test signals
Risks are brittle substitutions as audit message wording changes, regex portability, and hiding meaningful parser differences by over-normalizing. The key signal is a clean `diffcheck`; new audit samples should add or adjust substitutions deliberately.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auditd_raw.sed -->
