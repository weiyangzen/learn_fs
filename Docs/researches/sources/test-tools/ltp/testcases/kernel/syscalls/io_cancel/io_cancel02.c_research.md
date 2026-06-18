<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_cancel/io_cancel02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/io_cancel/io_cancel02.c

Purpose: Ported from Crackerjack to LTP by Masatake YAMATO <yamato@redhat.com> Test io_cancel invoked via libaio with one of the data structures points to invalid data and expects it to return -EFAULT.

Important APIs/types/functions: includes `config.h`, `tst_test.h`, `libaio.h`; touches `io_cancel`; defines `run`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner. Error-path assertions cover `EFAULT`.

State and persistence behavior: Runtime state is Linux AIO context identifiers and request/event pointers passed through syscall or libaio wrappers.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `config.h`, `tst_test.h`, `libaio.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_RET`, `TST_TEST_TCONF`. Expected errno values include `EFAULT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/io_cancel/io_cancel02.c -->
