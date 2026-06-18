<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/init_module/init_module02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/init_module/init_module02.c

Purpose:  Basic init_module() failure tests. [Algorithm] Tests various failure scenarios for init_module().

Important APIs/types/functions: includes `linux/capability.h`, `stdlib.h`, `errno.h`, `lapi/init_module.h`, `tst_module.h`, `tst_capability.h`; touches `init_module`, `munmap`; defines `setup`, `run`, `cleanup`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_FSTAT`, `SAFE_MMAP`, `SAFE_OPEN`.

Control flow centers on `setup`, `run`, `cleanup`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.setup`, `.cleanup`, `.needs_root` into the LTP runner. Error-path assertions cover `EEXIST`, `EFAULT`, `EINVAL`, `EKEYREJECTED`, `ENOEXEC`, `EPERM`.

State and persistence behavior: Runtime state is kernel module loading, module signature enforcement, CAP_SYS_MODULE permission, and module reference cleanup.

Dependencies and integration points: Depends on building init_module.ko, CAP_SYS_MODULE, kernel module loading policy, signature enforcement settings, and tst_module helpers. Direct include dependencies include `linux/capability.h`, `stdlib.h`, `errno.h`, `lapi/init_module.h`, `tst_module.h`, `tst_capability.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TCONF`, `TST_CAP`, `TST_CAP_DROP`, `TST_CAP_REQ`, `TST_EXP_FAIL`, `TST_PASS`, `TST_RET`. Expected errno values include `EEXIST`, `EFAULT`, `EINVAL`, `EKEYREJECTED`, `ENOEXEC`, `EPERM`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/init_module/init_module02.c -->
