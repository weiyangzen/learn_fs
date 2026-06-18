# sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/keyctl08.c

Purpose: CVE-2016-9604 regression checking that session keyrings beginning with `.` cannot be joined. The test calls `keyctl_join_session_keyring(".builtin_trusted_keys")` as root and expects failure with `EPERM`; success is reported as a security failure. State is only the process session keyring request. Dependencies are keyutils helper wrappers and root execution. Risks are typo in diagnostic text only; behavior is direct. Test signal is `EPERM` denial for the dot-prefixed builtin trusted keyring name.
