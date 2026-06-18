<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/lib.h -->
## sources/test-tools/liburing/src/lib.h

Purpose: central internal convenience header for liburing C sources. It normalizes declarations and optionally redirects libc allocation/memory primitives to liburing's nolibc replacements.

Important APIs/types/functions: defines `offsetof`, `container_of`, `__maybe_unused`, `__hot`, and `__cold` if absent. Under `CONFIG_NOLIBC`, it declares `__uring_memset`, `__uring_malloc`, and `__uring_free`, then remaps `malloc`, `free`, and `memset`.

Control flow: no runtime flow except through remapped allocation/memory calls when nolibc is enabled.

State and persistence behavior: no owned state. It affects which allocator backs probe allocation and setup/register helper memory paths.

Dependencies and integration points: included by `queue.c`, `setup.c`, `register.c`, `nolibc.c`, `syscall.c`, and `version.c`. It includes `config-host.h` to see build options.

Risks: macro remapping is global for translation units that include it, so new code must avoid relying on libc-only semantics in nolibc builds. Attribute and `container_of` definitions are low-level and should stay compatible with compiler expectations.

Test signals: successful build under normal and nolibc configurations is the main signal; runtime probe allocation and setup tests exercise remapped allocation.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/lib.h -->
