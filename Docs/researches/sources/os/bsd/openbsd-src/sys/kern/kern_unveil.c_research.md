# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_unveil.c

Read completely: 829 lines.

Implements the kernel side of OpenBSD `unveil(2)`: per-process pathname access restrictions tied to directory vnodes plus optional terminal component names. It manages unveil state across add, lookup, fork copy, process destroy, vnode removal, and namei enforcement.

Data model:
- `struct unveil` binds a directory vnode to either directory-wide permission flags or a red-black tree of named terminal children, plus a cover index and rwlock.
- `struct unvname` stores a terminal component name, its length, permission flags, and RBT linkage.
- Limits are fixed at `UNVEIL_MAX_VNODES` and `UNVEIL_MAX_NAMES`, both 128 per process.
- `vnode.v_uvcount` counts unveil references across processes and allows fast skip when no process has unveiled a vnode.

Name tree and lifecycle:
- `unvname_compare()`, `unvname_new()`, and `unvname_delete()` manage RBT keys by NUL-terminated component name and length.
- `unveil_add_name_unlocked()`, `unveil_add_name()`, and `unveil_namelookup()` insert and find terminal names under an unveiled directory.
- `unveil_delete_names()` removes all terminal names for an unveil entry under its lock.
- `unveil_destroy()` releases all vnode references, decrements `v_uvcount`, deletes names, frees the per-process array, and clears process counters.
- `unveil_copy()` duplicates parent unveil state into a child process, taking vnode references and copying every terminal name and flag.

Adding unveils:
- `unveil_parsepermissions()` translates `r`, `w`, `x`, and `c` permission strings into `UNVEIL_*` flags plus `UNVEIL_USERSET`.
- `unveil_add()` receives a resolved `nameidata`, allocates the process unveil array on first use, enforces vnode/name limits, chooses the directory vnode for either directory or terminal-component entries, references it, and updates existing or new unveil entries.
- Directory adds make the directory unrestricted by terminal-name filtering and replace `uv_flags`.
- Terminal adds create or update an `unvname` under the containing directory and increment the process name count only for new names.
- `unveil_add_vnode()` allocates the next process slot, initializes its lock/name tree, stores the directory vnode, computes its covering unveil, and refreshes any entries covered by the same ancestor.

Cover and lookup:
- `unveil_find_cover()` walks upward from a vnode toward the process root or `rootvnode`, crossing mount roots through `mnt_vnodecovered`, and returns the nearest covering unveil slot.
- `unveil_lookup()` finds a process unveil entry for a vnode, using `v_uvcount == 0` as a fast negative check.
- `unveil_covered()` moves a match upward to its cover when path lookup traverses `..`.
- `unveil_start_relative()` initializes `ni_unveil_match` for relative lookups, either from the starting vnode or by walking up to a cover.
- `unveil_check_component()` updates the current unveil match while namei traverses intermediate directories, handling `..` specially.

Final enforcement:
- `unveil_check_final()` runs after successful final-component lookup. It bypasses checks for pledge's own unveil operation, absent unveil state, or `BYPASSUNVEIL`.
- Directory terminal matches require a vnode unveil with user-set flags and matching requested access.
- Non-directory terminal matches first check an exact named child under the parent directory, then directory-wide flags, then any covering matches found during traversal.
- Access mismatch sets `AUNVEIL` in accounting flags and returns `EACCES` when a visible unveil entry exists with some permission mask, or `ENOENT` when the path should appear hidden.

Vnode removal:
- `unveil_removevnode()` scans active processes for entries referencing a vnode being removed, nulls those entries, clears flags, releases references, decrements `v_uvcount`, and leaves holes for later lookup behavior.
