# sources/test-tools/ltp/testcases/kernel/syscalls/io_pgetevents/Makefile

Purpose: adds AIO libraries where required and includes LTP leaf build rules.

Important APIs/types/functions: make variables and includes are the important interface here: `LDLIBS			+= $(AIO_LIBS)`.

Control flow: this file has no runtime control flow; it participates in the LTP build by setting local variables before including shared make fragments.

State and persistence behavior: build-time only. It does not create kernel state, but it controls whether test binaries are linked with helper libraries and whether auxiliary scripts are installed.

Dependencies and integration points: integrates with the AIO completion path, optional signal-mask replacement, and 32-bit/time64 timeout ABI variants; downstream tests depend on these variables to find LTP headers, common rules, libaio/newipc/ipc helper libraries, or installed helper scripts.

Risks: incorrect linkage or filtering turns into compile-time/link-time failures or skipped binaries rather than runtime assertion failures.

Test signals: successful `make` in the directory should build the expected test programs and install any declared helper targets.
