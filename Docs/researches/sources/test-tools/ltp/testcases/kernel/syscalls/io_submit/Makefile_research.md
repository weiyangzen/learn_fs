# sources/test-tools/ltp/testcases/kernel/syscalls/io_submit/Makefile

Purpose: adds AIO libraries where required and includes LTP leaf build rules.

Important APIs/types/functions: make variables and includes are the important interface here: `io_submit01:	LDLIBS	+= $(AIO_LIBS)`.

Control flow: this file has no runtime control flow; it participates in the LTP build by setting local variables before including shared make fragments.

State and persistence behavior: build-time only. It does not create kernel state, but it controls whether test binaries are linked with helper libraries and whether auxiliary scripts are installed.

Dependencies and integration points: integrates with submission of raw or libaio `iocb` requests and completion harvesting; downstream tests depend on these variables to find LTP headers, common rules, libaio/newipc/ipc helper libraries, or installed helper scripts.

Risks: incorrect linkage or filtering turns into compile-time/link-time failures or skipped binaries rather than runtime assertion failures.

Test signals: successful `make` in the directory should build the expected test programs and install any declared helper targets.
