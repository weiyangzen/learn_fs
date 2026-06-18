# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_sysctl.c

Read completely: 2869 lines.

Implements the native NetBSD sysctl subsystem: the global sysctl tree, sysctl syscall dispatch, dynamic node create/destroy/query/describe operations, kernel convenience APIs, teardown logs, user/kernel copy wrappers, version conversion, generic helpers, and address hashing support.

Core state:
- `sysctl_root` is the root node of the native tree, initially read/write and numbered from `CREATE_BASE`.
- `sysctl_treelock` serializes tree access; comments note this lock is broad and held across allocation/copy operations.
- `sysctl_file_marker_lock` supports file-related sysctl marker users elsewhere.
- Kernel attributes stored here include `hostname`, `domainname`, `hostid`, and `defcorename`.
- `M_SYSCTLNODE` and `M_SYSCTLDATA` back node and sysctl-data allocations.

Initialization:
- `sysctl_init()` initializes the tree lock, root base node, all link-set sysctl setup functions, and the file marker lock.
- `sysctl_finalize()` marks the root permanent, preventing later permanent-node additions and enforcing read-only tree policy.
- `sysctl_copyin()`, `sysctl_copyout()`, and `sysctl_copyinstr()` abstract user vs kernel callers and emit ktrace MIB I/O records for user callers.

Syscall and dispatch:
- `sys___sysctl()` copies in the MIB and old length, locks the tree as writer if a new value is supplied, calls `sysctl_dispatch()`, unlocks, copies out the final length, and maps insufficient old buffer space to `ENOMEM`.
- `sysctl_lock()`, `sysctl_relock()`, and `sysctl_unlock()` manage read/write locking and mark the current LWP with `LP_SYSCTLWRITE`.
- `sysctl_dispatch()` locates the target node, enforces private-node read permission on final targets, invokes node-specific handlers, generic lookup, or meta-operations such as `CTL_QUERY`, `CTL_CREATE`, `CTL_DESTROY`, `CTL_MMAP`, and `CTL_DESCRIBE`.

Tree traversal and query:
- `sysctl_locate()` walks child arrays by numeric MIB component, handles private traversal checks, supports `CTLFLAG_ANYNUMBER`, follows aliases up to a bounded depth, and returns the last node plus consumed component count.
- `sysctl_query()` copies out `struct sysctlnode` descriptions under a node, merges emulation overlay trees, and supports version checks.
- `sysctl_cvt_in()` and `sysctl_cvt_out()` currently support `SYSCTL_VERSION`/`SYSCTL_VERS_1` node layout only.

Create, destroy, and lookup:
- `sysctl_create()` validates authorization, tree mutability, parent type, node name, number, type, flags, immediate/owned-data constraints, sizes, collisions, aliases, dynamic numbering, and optional symbol resolution. It allocates/grows child arrays, inserts the node in numeric order, reparents moved children, updates version numbers up to the root, and returns the created node description.
- `sysctl_destroy()` validates authorization and mutability, finds the requested child by number/name/version, refuses permanent or non-empty nodes, frees owned data/descriptions, compacts the child array, frees empty child arrays, updates versions, and returns the removed node description.
- `sysctl_lookup()` implements ordinary read/write of terminal values with private and modify authorization checks, exact-size writes for bool/int/quad/struct, bounded string writes with NUL handling, immediate-value support, and entropy mixing of new written data via `rnd_add_data()`.

Other tree operations:
- `sysctl_mmap()` forwards mmap-style requests only to nodes with `CTLFLAG_MMAP` and a handler.
- `sysctl_describe()` gets or sets node descriptions, with authorization and mutability checks, owned-description allocation, and packed `sysctldesc` copyout.
- `sysctl_free()` recursively frees a tree's owned data, descriptions, and child arrays.
- `old_sysctl()` bridges old in-kernel callers to the new dispatch path.

Kernel create/destroy convenience API:
- `sysctl_createv()` builds a node from varargs MIB components, calls `sysctl_create()`, treats compatible `EEXIST` as success, optionally returns the actual node pointer, logs dynamic nodes for later teardown, and attaches descriptions.
- `sysctl_destroyv()` locates and removes a node, treating missing nodes and non-empty parent nodes as successful cleanup cases.
- `sysctl_log_add()`, `sysctl_log_realloc()`, `sysctl_log_print()`, and `sysctl_teardown()` record dynamically created nodes in reverse-MIB form and remove them during module/device teardown.

Generic helpers and memory management:
- `sysctl_needfunc()` warns and returns static data for nodes that should have had a custom handler.
- `sysctl_notavail()` supports query but otherwise returns `EOPNOTSUPP`.
- `sysctl_null()` returns an empty result.
- `sysctl_map_flags()` translates flag words through a map table.
- `sysctl_alloc()` and `sysctl_realloc()` allocate and grow child-node arrays while maintaining parent pointers.

Address hashing:
- `hash_value_ensure_initialized()` initializes a secret 32-byte key once from `cprng_strong()`.
- `hash_value()` hashes arbitrary input with keyed BLAKE2s for address/value obfuscation users.

Concurrency and notes:
- The tree lock is global and intentionally simple; the file itself warns that holding it across allocations and copyout is problematic.
- Kernel-created dynamic nodes are not guaranteed stable by pointer for long after unlock unless the caller controls teardown.
- `sysctl_lookup()` may fault if a kernel-created node references later-invalid external data.
- Description privacy filtering contains a surprising negated kauth condition in the read loop; verify intended `kauth_authorize_system()` semantics before relying on it for private description visibility.
