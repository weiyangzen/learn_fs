<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gethostbyname_r/gethostbyname_r01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/gethostbyname_r/gethostbyname_r01.c

Purpose:  Test for GHOST: glibc vulnerability (CVE-2015-0235). https://www.qualys.com/research/security-advisories/GHOST-CVE-2015-0235.txt

Important APIs/types/functions: includes `tst_test.h`; touches `gethostbyname_r`; defines `check_vulnerable`.

Control flow centers on `check_vulnerable`. The `struct tst_test` registration wires `.test_all` into the LTP runner. Error-path assertions cover `ERANGE`.

State and persistence behavior: Runtime state is libc resolver scratch buffers and result pointers; the test targets buffer sizing/error behavior rather than kernel state.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TST_EXP_EQ_LI`. Expected errno values include `ERANGE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gethostbyname_r/gethostbyname_r01.c -->
