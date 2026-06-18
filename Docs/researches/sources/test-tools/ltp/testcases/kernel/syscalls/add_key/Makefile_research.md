# sources/test-tools/ltp/testcases/kernel/syscalls/add_key/Makefile

Purpose: LTP leaf Makefile for Linux key retention service `add_key()` tests. It includes standard testcase make rules, appends `$(KEYUTILS_LIBS)` to `LDLIBS`, and delegates targets to `generic_leaf_target.mk`. Runtime requirements include root, key quotas, user management commands, and key type support declared per C file. State is build-only. Dependency risk is missing keyutils library settings causing link failure. Test signal is successful build of all `add_key0*.c` programs.
