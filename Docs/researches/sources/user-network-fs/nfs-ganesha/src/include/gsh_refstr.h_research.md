# sources/user-network-fs/nfs-ganesha/src/include/gsh_refstr.h

Purpose: This header defines an RCU-friendly refcounted string object used for shared paths and other mutable pointer-to-string configuration.

Important APIs/types/functions: `struct gsh_refstr` contains a `urcu_ref` and flexible string buffer. `gsh_refstr_alloc` allocates a buffer of caller-specified length. Inline `gsh_refstr_dup` duplicates a C string. `gsh_refstr_release` is the refcount release callback. `gsh_refstr_get` increments a nonzero refcount using `urcu_ref_get_unless_zero` when available or a compare/exchange fallback. `gsh_refstr_put` releases references.

Control flow: Writers publish/replace pointers under RCU-style discipline. Readers fetch a pointer, take a reference while protected, use `gr_val`, then put it.

State and persistence: Refcounted strings are in-memory lifetime-managed state. In this subset they are important for `req_op_context` fullpath/pseudopath references that remain valid during an operation even if exports are updated.

Dependencies and integration points: Depends on liburcu refcount APIs, atomics, and standard string allocation headers. Used by export/op-context path management and any shared string needing stable references.

Risks: `gsh_refstr_get` aborts if the refcount is zero or wraps, so callers must obey RCU/ref ownership rules. Allocation lengths must include the terminating NUL. Forgetting puts leaks path/config strings.

Test signals: Test duplicate contents, concurrent get/put under RCU, fallback compare/exchange path if supported, zero-ref protection, release callback freeing, and op-context path replacement scenarios.
