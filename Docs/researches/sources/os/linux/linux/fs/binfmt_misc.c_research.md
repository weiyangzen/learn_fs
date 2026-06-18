# File Research: sources/os/linux/linux/fs/binfmt_misc.c

Purpose: Implements the `binfmt_misc` filesystem and binary-format loader, allowing userspace to register executable handlers by filename extension or file magic.

Main structures and state:
- `Node`: one registered handler, including list linkage, flags, magic/extension, optional mask, interpreter path, dentry, optional pinned interpreter file, and a refcount used to synchronize removal with exec.
- `struct binfmt_misc`: per-user-namespace registry reached through `user_ns->binfmt_misc`, with an enabled flag, handler list, and list rwlock.
- `misc_format`: Linux binary format registered through `insert_binfmt()`.
- `bm_fs_type`: `binfmt_misc` pseudo filesystem, mountable in user namespaces.

Execution flow:
- `load_binfmt_misc()` finds the nearest mounted `binfmt_misc` instance from the current user namespace upward, falling back to `init_binfmt_misc`.
- `search_binfmt_handler()` scans enabled entries and matches either extension or magic/mask bytes in `bprm->buf`.
- `get_binfmt_handler()` takes a refcount under `entries_lock`; `put_binfmt_handler()` closes pinned interpreter files and frees the handler when the last exec/removal user drops it.
- `load_misc_binary()` rewrites arguments for the interpreter, handles preserve-argv0/open-binary/credential flags, opens or clones the interpreter file, and stores it in `bprm->interpreter`.

Registration and control interface:
- `/register` accepts strings shaped like `:name:type:offset:magic:mask:interpreter:flags`.
- `create_entry()` validates names, parses `E` extension or `M` magic entries, decodes `\x` hex escapes, validates magic length against `BINPRM_BUF_SIZE`, and parses flags `P`, `O`, `C`, and `F`.
- `/status` accepts `0`, `1`, or `-1` to disable, enable, or clear all handlers.
- Per-entry files accept the same commands to disable, enable, or delete one handler.
- `entry_status()` reports interpreter, flags, and extension or hex-encoded magic/mask details.

Namespace and filesystem behavior:
- `bm_fill_super()` lazily allocates one `binfmt_misc` registry per user namespace and publishes it with release semantics paired with loader-side acquire reads.
- The filesystem uses `simple_fill_super()` to expose `status` and `register`; entries are persistent dentries created by `add_entry()`.
- `bm_evict_inode()` removes list entries during inode eviction and releases the handler reference.
- `remove_binfmt_handler()` removes the list entry and recursively removes the dentry.

Concurrency and safety:
- The root inode lock serializes register/remove operations, while `entries_lock` protects the handler list against concurrent exec lookup.
- Refcounting prevents a handler from being freed while `load_misc_binary()` is using it.
- `MISC_FMT_OPEN_FILE` opens the interpreter at registration time using the credentials that opened `/register`, important for unprivileged mounts.
- `BINPRM_FLAGS_PATH_INACCESSIBLE` is rejected because the interpreter must be able to access the target binary after exec.

Risk notes: This file sits on the exec path and exposes a writable control filesystem. Parser validation, namespace publication ordering, handler refcounting, and interpreter credential handling are the critical correctness and security points.
