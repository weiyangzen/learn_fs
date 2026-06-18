# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_varsym.c

Implements variable storage and substitution for variant symlinks, plus syscalls to set/get/list variable symbols at process, user, system, and prison scopes.

Key structures:
- Global `varsymset_sys`.
- Per-set TAILQ of `varsyment`, each referencing a refcounted `varsym`.
- Each `varsymset` has a lock and set-size accounting.

Key APIs:
- `varsymreplace()`
- `sys_varsym_set()`
- `sys_varsym_get()`
- `sys_varsym_list()`
- `varsymfind()`
- `varsymmake()`
- `varsymdrop()`
- `varsymset_init()`
- `varsymset_clean()`

Important behavior:
- `varsym_sysinit()` initializes the global system varsym set.
- `varsymreplace()` scans a symlink target for `${name}` expressions, looks up variables using `VARSYM_ALL_MASK`, substitutes values in-place, and rejects expansion beyond the target buffer.
- `sys_varsym_set()` copies in name/data, applies privilege checks for system/prison-level variables, maps system-level requests in jail to prison scope, and creates or deletes variables.
- `sys_varsym_get()` resolves a wildcard/name using a mask, copies out the value if the buffer is large enough, and returns `EOVERFLOW` with an empty string when too small.
- `sys_varsym_list()` enumerates a chosen scope using a user-supplied marker, copying name/value NUL-terminated pairs into a buffer and returning bytes copied.
- `varsymfind()` searches scopes in order: process, user, then prison/system depending on jail state, retaining the returned symbol.
- `varsymmake()` creates a new varsym entry or deletes an existing one. The syscall path first deletes any old value before inserting replacement.
- `varsymset_init()` can duplicate references from an existing set without copying string storage.
- `varsymset_clean()` removes all entries and drops refs.

Concurrency model:
- Each varsym set uses `lockmgr` shared/exclusive locking.
- Symbols have atomic refcounts so lookups can safely retain across lock release.

Filesystem relevance:
- Directly filesystem-relevant: `varsymreplace()` is called from namei/path resolution for variant symlink expansion. These variables alter resolved symlink targets based on process/user/system/prison state.
