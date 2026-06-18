<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/init_module/init_module.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/init_module/init_module.c

Purpose: Dummy kernel module used by init_module syscall tests; it accepts a status parameter and fails initialization when status is invalid.

Important APIs/types/functions: includes `linux/module.h`, `linux/init.h`, `linux/proc_fs.h`, `linux/kernel.h`; defines `dummy_init`, `dummy_exit`.

Control flow centers on `dummy_init`, `dummy_exit`. Error-path assertions cover `EINVAL`.

State and persistence behavior: Runtime state is kernel module loading, module signature enforcement, CAP_SYS_MODULE permission, and module reference cleanup.

Dependencies and integration points: Depends on building init_module.ko, CAP_SYS_MODULE, kernel module loading policy, signature enforcement settings, and tst_module helpers. Direct include dependencies include `linux/module.h`, `linux/init.h`, `linux/proc_fs.h`, `linux/kernel.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals come from consumers of this helper and from compile-time availability checks. Expected errno values include `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/init_module/init_module.c -->
