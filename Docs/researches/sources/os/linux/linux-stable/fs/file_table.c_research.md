# File Research: sources/os/linux/linux-stable/fs/file_table.c

This file manages global `struct file` allocation, initialization, accounting, freeing, and final `fput()` teardown. It is separate from `file.c`: `file.c` manages descriptor tables, while this file manages the file objects those descriptors point to.

Major responsibilities:
- Maintain global file count accounting and sysctls: `file-nr`, `file-max`, and `nr_open`.
- Allocate normal files, unaccounted internal files, backing files, pseudo files, and cloned files.
- Initialize `struct file` fields, credentials, security blobs, fsnotify mode, read/write capability bits, mappings, and refcounts.
- Support backing files that carry a separate user-visible path and optional security state.
- Tear down files in `__fput()`: fsnotify close, epoll release, locks, LSM release, fasync, filesystem release op, cdev refs, file operations, ownership, path, mount, and credentials.
- Defer final `fput()` through task work where possible, or delayed work when needed.
- Initialize file slabs and the default global max-files value at boot.

Important design points:
- The `filp` and `bfilp` caches are `SLAB_TYPESAFE_BY_RCU`, so file initialization sets `f_ref` last.
- `alloc_empty_file()` enforces `file-max` for unprivileged users; internal no-account variants set `FMODE_NOACCOUNT`.
- Pseudo files allocate pseudo dentries and default to suppressing fsnotify events.
- `fput()` defers cleanup unless synchronous variants are requested.
- Kernel threads should use synchronous fput only when carefully justified, because normal delayed fput can interact with unmount dependencies.

Key invariants:
- Callers assigning writable mounts to newly allocated files are responsible for balancing mount writer counts.
- `FMODE_OPENED` gates the full release path; unopened files can be freed directly.
- Backing files must free security state and drop their stored user path.
- `fput_close()` and `fput_close_sync()` are optimized for known-last-reference close paths.
- `files_init()` must create slab caches before file allocation can occur.

External interfaces:
- Exports file allocation helpers, backing file helpers, `fput`, `__fput_sync`, `flush_delayed_fput`, and max-file accessors.
