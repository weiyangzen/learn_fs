# sources/user-network-fs/s3fs-fuse/src/fdcache_pseudofd.h

Purpose: Declares `PseudoFdManager`, the global allocator for pseudo-fd integers.

Important APIs and types: `pseudofd_list_t` is a vector of active pseudo-fds. Public static APIs are `Get` and `Release`. The singleton constructor/destructor are private; copying and moving are disabled.

Control flow contract: Call `Get` when a pseudo-fd is created and `Release` exactly once when it is destroyed. All internal list access is guarded by `pseudofd_list_lock`.

State and persistence behavior: No disk state; live process state only.

Dependencies and integration points: Included by `fdcache_fdinfo.cpp`; uses thread-safety annotations from `common.h`.

Risks: The API does not encode ownership, so correctness depends on `PseudoFdInfo` lifecycle. Duplicate release returns false but does not otherwise repair callers.

Test signals: Open/close lifecycle and pseudo-fd duplication paths are the relevant integration signals.
