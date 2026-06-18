## sources/security-integrity/libcap/libcap/cap_alloc.c

Purpose: allocation, duplication, initialization, and freeing support for `cap_t`, `cap_iab_t`, launcher objects, and libcap-managed strings.

Important APIs/functions: constructor `_libcap_initialize()`, `cap_max_bits()`, `_libcap_strdup()`, `cap_init()`, `cap_dup()`, `cap_iab_init()`, `cap_iab_dup()`, `cap_new_launcher()`, `cap_func_launcher()`, and `cap_free()` in the latter part of the file.

Control flow: constructor initializes syscall routing and discovers runtime kernel capability count via `cap_get_bound` binary search. Allocators allocate a tagged `struct _cap_alloc_s` envelope, set magic/size, initialize kernel capability version, and return the embedded public opaque pointer. Duplicators validate magic, allocate a new object, lock/copy source content, and unlock. Launcher creation stores argv/env/callback fields and security-change flags. `cap_free()` validates back-pointer magic and releases strings, cap sets, IABs, and launchers.

State/persistence: process-global `_cap_max_bits` and init mutex; heap-managed opaque objects with magic tags; no persistent files.

Dependencies/integration: `libcap.h` internals, `cap_set_syscall`, `cap_get_bound`, kernel `capget`, atomic mutex macros. Public APIs declared in `sys/capability.h`.

Risks: callers must free only libcap-managed pointers; global initialization is constructor-order sensitive; `cap_proc_root` strings use same freeing contract; launcher stores argv/env pointers rather than deep-copying all arrays, so caller lifetimes matter.

Test signals: `cap_test` allocation/free bad-pointer checks, launcher allocation tests, and leak/error-path tests for `cap_free` on all magic types.
