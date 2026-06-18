# sources/test-tools/ltp/testcases/kernel/syscalls/ioperm/Makefile

Purpose: targeted syscall behavior in the LTP kernel/syscalls suite.

Important APIs/types/functions: make variables and includes are the important interface here: `top_srcdir, testcases.mk, generic_leaf_target.mk`.

Control flow: this file has no runtime control flow; it participates in the LTP build by setting local variables before including shared make fragments.

State and persistence behavior: build-time only. It does not create kernel state, but it controls whether test binaries are linked with helper libraries and whether auxiliary scripts are installed.

Dependencies and integration points: integrates with x86 I/O-port permission bitmap changes and privilege checks; downstream tests depend on these variables to find LTP headers, common rules, libaio/newipc/ipc helper libraries, or installed helper scripts.

Risks: incorrect linkage or filtering turns into compile-time/link-time failures or skipped binaries rather than runtime assertion failures.

Test signals: successful `make` in the directory should build the expected test programs and install any declared helper targets.
