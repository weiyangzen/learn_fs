## sources/security-integrity/libcap/libcap/cap_file.c

Purpose: reads and writes Linux file capability xattrs for path and file-descriptor APIs.

Important APIs/functions: `cap_get_fd()`, `cap_get_file()`, `cap_set_fd()`, `cap_set_file()`, `cap_get_nsowner()`, `cap_set_nsowner()`, internals `_fcaps_load()` and `_fcaps_save()`.

Control flow: get paths allocate a `cap_t`, read `security.capability` xattrs into `vfs_ns_cap_data`, validate revision/size, convert endian fields, and set effective bits when the file effective flag is present. Set paths validate regular non-symlink files, convert internal caps to VFS v1/v2/v3 format, enforce all-or-none effective flag semantics, and set/remove xattrs. `cap_set_file()` first uses `O_RDONLY|O_NOFOLLOW`; if unreadable, it opens `O_PATH|O_NOFOLLOW`, validates with `fstat`, and writes via `/proc/self/fd/<fd>` to avoid filename replacement races.

State/persistence: persists file xattrs and namespace rootid in v3 capabilities; mutates caller `cap_t` rootid for namespace owner setters.

Dependencies/integration: Linux xattr syscalls, VFS capability UAPI structs, byte-order handling, `/proc/self/fd`, regular file semantics.

Risks: the `cap_get_file()` short-read branch contains a duplicated `cap_free(result)` call, which is a potential double-free if reached; file xattr writes require careful privilege and filesystem support; `O_PATH` fallback depends on procfs availability.

Test signals: path/fd get/set/remove tests, symlink/non-regular rejection, rootid v3 round trips, unreadable regular-file path race tests, and `compare-cap.go` file capability checks.
