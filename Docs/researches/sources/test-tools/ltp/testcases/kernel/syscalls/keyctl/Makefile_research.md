# sources/test-tools/ltp/testcases/kernel/syscalls/keyctl/Makefile

Purpose: builds the key management syscall tests. It includes LTP testcase rules, adds `$(KEYUTILS_LIBS)` globally, and links `keyctl02` with `-lpthread` for its read/revoke race. Runtime behavior is in the C files; build state is library linkage for keyutils wrappers such as `add_key`, `request_key`, and `keyctl_join_session_keyring`. Integration risk is missing keyutils development libraries or pthread linkage. Test signal is successful compilation/linking of all `keyctl*.c` tests through `generic_leaf_target.mk`.
