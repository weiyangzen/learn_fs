<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/syscall.h -->
## sources/test-tools/liburing/src/syscall.h

Purpose: centralizes low-level syscall wrapper declarations and error-pointer helpers used by liburing sources.

Important APIs/types/functions: `ERR_PTR`, `PTR_ERR`, and `IS_ERR` encode negative errno values as pointer values for mmap-like helpers. Declares `__sys_io_uring_register`, `__sys_io_uring_setup`, `__sys_io_uring_enter`, `__sys_io_uring_enter2`, `__sys_mmap`, `__sys_munmap`, `__sys_madvise`, `__sys_getrlimit`, `__sys_setrlimit`, `__sys_close`, and `get_page_size`.

Control flow: implementation lives elsewhere in platform syscall code; this header standardizes call sites.

State and persistence behavior: no state. Helpers interpret syscall results and pointer-encoded errors.

Dependencies and integration points: included by setup, queue, register, nolibc, and syscall translation units. It includes system resource/mman headers and public liburing declarations.

Risks: `ERR_PTR`/`IS_ERR` rely on negative errno range and pointer casts. Incorrect normalization would cause mmap failures to be treated as valid mappings or valid low addresses as errors.

Test signals: setup memory mapping, registered resource operations, and nolibc allocation all exercise this layer.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/syscall.h -->
