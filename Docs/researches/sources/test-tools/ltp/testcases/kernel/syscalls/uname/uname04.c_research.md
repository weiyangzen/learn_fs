<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/uname/uname04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/uname/uname04.c

Purpose: Check that memory after the string terminator in all the utsname fields has been zeroed. cve-2012-0957 leaked kernel memory through the release field when the UNAME26 personality was set. Thanks to Kees Cook for the original proof of concept: http://www.securityfocus.com/bid/55855/info

Important APIs/types/functions: includes `string.h`, `sys/utsname.h`, `tst_test.h`, `lapi/personality.h`; exercises `uname`; defines `check_field`, `try_leak_bytes`, `run`.

Control flow centers on `check_field`, `try_leak_bytes`, `run`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.tags` into the runner. Named case hints include `CVE`.

State and persistence behavior: Runtime state is kernel utsname data and architecture/personality-dependent field length handling.

Dependencies and integration points: Depends on libc `uname()`, personality flags for old-uts behavior, and bad-address helpers for EFAULT coverage. Direct include dependencies include `string.h`, `sys/utsname.h`, `tst_test.h`, `lapi/personality.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/uname/uname04.c -->
