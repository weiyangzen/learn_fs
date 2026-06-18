# File Research: sources/os/plan9/9front/sys/src/9/port/chan.c

Core Plan 9 channel, path, mount, walk, and name-resolution implementation.

Key behavior:
- Provides refcount helpers, kernel string duplication/copy helpers, channel device reset/init/shutdown dispatch, and `Chan` allocation/freeing.
- `newpath`, `copypath`, `pathclose`, `fixdotdotname`, `uniquepath`, and `addelem` maintain channel path strings and undo `..` components.
- Channel close supports queued close work through a dedicated close process, allowing `ccloseq` to defer device close operations.
- `cunique` clones a channel if it is shared by reference.
- `eqchan` and `eqchantdqid` compare channels by type/dev/qid with optional version skipping.
- Mount handling includes `newmhead`, `putmhead`, `cmount`, `cunmount`, mount ordering, union mount handling, and mount cache invalidation.
- `findmount`, `domount`, and `undomount` translate between mounted channels and underlying channels during walk/name resolution.
- `ewalk` wraps device walk operations and preserves path state.
- `walk` resolves a list of path elements with mount traversal and optional no-mount behavior.
- `namec` is the central name resolver for open, create, remove, access, and stat-style operations; it parses names, handles roots and device names, walks components, enforces permissions, performs create/open/remove/truncation behavior, and returns a prepared channel.
- Name validation helpers reject empty, overlong, or invalid names using the `isfrog` character table.
- `isdir` enforces directory channels and `dirchanstat` stats directory channels.

Notable dependencies:
- Device table operations, mount heads, process namespace state, path and channel structures from `portdat.h`.
- Error handling, permission checks, and cache invalidation hooks.

Research notes:
- This is one of the central VFS files: small semantic changes can affect all file namespace operations.
- Locking spans channel refs, mount table state, path refs, and deferred close queues; error unwinding is pervasive.
- `namec` is the highest-risk function due to its many modes and interactions with mount points, creates, removes, and open flags.
