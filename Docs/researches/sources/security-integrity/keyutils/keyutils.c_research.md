<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/keyutils.c -->
# sources/security-integrity/keyutils/keyutils.c

## Purpose

`keyutils.c` is the libkeyutils implementation layer. It exposes weak syscall wrappers for `add_key`, `request_key`, and `keyctl`, typed wrappers for individual keyctl commands, allocated-buffer convenience helpers, recursive keyring traversal, type/description lookup, capability emulation for older kernels, and optional key-specific strerror/perror overrides.

## Important APIs, Types, and Functions

Weak wrappers call `__NR_add_key`, `__NR_request_key`, and `__NR_keyctl`. Typed wrappers cover keyring ID/session join, update, revoke, chown, setperm, describe, clear, link/unlink, search, read, instantiate/negate/reject, request-key defaults, timeout, authority, security label, parent-session installation, invalidate, persistent keyrings, DH/KDF, restrict, pkey query/encrypt/decrypt/sign/verify, move, capabilities, and watch. Allocation helpers are `keyctl_describe_alloc()`, `keyctl_read_alloc()`, `keyctl_get_security_alloc()`, and `keyctl_dh_compute_alloc()`. Traversal helpers are `recursive_key_scan()`, `recursive_session_key_scan()`, and `find_key_by_type_and_desc()`.

## Control Flow

Most wrappers are thin one-line `keyctl()` calls. Compatibility paths fall back from `KEYCTL_REJECT` to negate and from `KEYCTL_INSTANTIATE_IOV` to a concatenated buffer when the kernel returns `EOPNOTSUPP`. Capability emulation probes individual operations when `KEYCTL_CAPABILITIES` is not available. Alloc helpers first query required length, allocate, retry, and loop if a variable-sized result grows. Recursive scanning describes a key, reads child IDs for keyrings, depth-first scans children, then calls the user callback for the current key. Name lookup first tries `request_key()` and then scans `/proc/keys` with a confirming `keyctl_describe()`.

## State and Persistence Behavior

The library does not persist data itself, but it mutates kernel keyring state through syscall wrappers. Alloc helpers return heap buffers owned by callers. Recursive scans and lookup read key descriptions and keyring payloads from the kernel. Optional error override mode keeps function pointers resolved from `RTLD_NEXT`.

## Dependencies and Integration Points

The file depends on Linux keyring syscalls, `sys/uio.h` for instantiate-iov, `/proc/keys` for fallback lookup, `dlfcn.h` under `NO_GLIBC_KEYERR`, and `keyutils.h` ABI definitions. It backs the `keyctl` executable, request-key helper, tests, and external applications linking `libkeyutils`.

## Risks and Edge Cases

Thin syscall wrappers trust caller-provided pointers and lengths. IOV fallback can overflow `size_t` if a malicious caller passes huge segment lengths. Alloc helpers can race with changing key contents and must retry; callers must free results. `/proc/keys` fallback depends on procfs format and visibility. Capability emulation probes with invalid IDs and infers support from errno, which can be imperfect under policy restrictions. The optional `strerror_r()` override contains a debug `printf("hello")`, making that build mode noisy.

## Test Signals

The shell suite exercises most wrappers through `keyctl`. Direct library validation should compile/link consumers, test fallback behavior on older kernels, verify allocated-buffer growth races, scan recursive keyrings, and compare `supports` output with expected kernel capabilities.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/keyutils.c -->
