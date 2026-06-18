<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gethostname/gethostname02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/gethostname/gethostname02.c

Purpose:  Verify that gethostname(2) fails with - ENAMETOOLONG when len is smaller than the actual size

Important APIs/types/functions: includes `tst_test.h`; touches `gethostname`; defines `verify_gethostname`; uses LTP safe helpers such as `SAFE_GETHOSTNAME`.

Control flow centers on `verify_gethostname`. The `struct tst_test` registration wires `.test_all` into the LTP runner. Error-path assertions cover `ENAMETOOLONG`.

State and persistence behavior: Runtime state is the kernel hostname copied into user buffers of different sizes.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_FAIL`. Expected errno values include `ENAMETOOLONG`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gethostname/gethostname02.c -->
