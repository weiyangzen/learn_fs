# sources/security-integrity/libcap/pam_cap/test_pam_cap.c

Purpose: inline unit/integration test for `pam_cap.c` using synthetic PAM, passwd, and group functions.

Important APIs/functions: stubs `pam_get_user()`, `pam_get_item()`, `pam_set_data()`, `getgrouplist()`, `getgrgid()`, and `getpwnam()` to control identities. `load_vectors()` captures ambient, bounding, and inheritable low 64-bit state. `test_arg_parsing()` validates every supported module option.

Control flow: performs non-privileged parser/config smoke tests first, clears inheritable state, skips privileged vector tests unless UID 0, then runs auth and setcred for a selected user and compares observed A/B/I vectors against command-line expectations.

State and dependencies: mutates real process capabilities for privileged tests and uses libcap APIs. Static globals hold current synthetic user and group/passwd records.

Risks and test signals: catches config matching order, unknown user handling, `/dev/null` no-policy behavior, no-user `PAM_INCOMPLETE`, IAB parsing/application, and fallback behavior. Deferred `pam_set_data()` is stubbed to fail after freeing data, so success of deferred application itself is not proven here.
