## sources/user-network-fs/pyfuse3/examples/passthroughfs.py

Purpose: Trio-based pyfuse3 passthrough filesystem that mirrors and mutates an underlying directory tree.

Important APIs/types/functions: `Operations` maps FUSE inode ids to paths and file descriptors. It implements lookup, getattr, forget, readlink, directory ops, unlink/rmdir, symlink, rename, hardlink, setattr, mknod, mkdir, statfs, open/create, read/write, and release. Helpers include `_inode_to_path`, `_add_path`, `_getattr`, and `_forget_path`.

Control flow: `main` parses source/mountpoint/debug/writeback options, creates operations, initializes FUSE, runs `trio.run(pyfuse3.main)`, and closes. FUSE calls translate inode/fh operations to Python `os.*` calls, converting `OSError.errno` to `FUSEError`. Lookup/readdir add path mappings; forget and deletion remove them; open/create maintain fd/inode/open-count maps.

State and persistence: Persistent state is the underlying source directory. In-memory state tracks inode-to-path mapping, lookup counts, open fd maps, and hardlink path sets. Attribute and entry timeouts are zero, reducing cache staleness.

Dependencies and integration: Demonstrates broad pyfuse3 API coverage, Trio, native POSIX filesystem calls, FUSE request context uid/gid/umask, and optional writeback-cache configuration storage.

Risks and test signals: The file documents known risks: possible tree escape, weak behavior when underlying files are renamed/deleted externally, slow full-directory reads, non-POSIX readdir offsets for hardlinks, and simplified block/generation attributes. Tests should mount a temp tree and exercise create/read/write/truncate/chmod/chown/timestamps/link/symlink/rename/unlink/rmdir/statfs/readdir/forget, plus external mutation behavior and hardlink directory ordering.
