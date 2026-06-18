<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom_var.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom_var.h

Purpose: Variant helper for testing both the raw getrandom syscall and libc getrandom when available.

Important APIs/types/functions: includes `lapi/syscalls.h`; touches `getrandom`, `raw syscall path`; defines `do_getrandom`, `getrandom_info`.

Control flow centers on `do_getrandom`, `getrandom_info`.

State and persistence behavior: Runtime state is kernel randomness/entropy availability and caller buffers filled by getrandom.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals come from consumers of this helper and from compile-time availability checks.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom_var.h -->
