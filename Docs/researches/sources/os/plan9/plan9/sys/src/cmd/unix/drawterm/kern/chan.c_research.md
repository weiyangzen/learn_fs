# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/chan.c

Drawterm’s Plan 9 channel, pathname, mount, and namespace resolver implementation.

Key responsibilities:
- Manages `Chan` and `Cname` allocation, reference counts, clone/close/free, copy-on-write uniqueness, and debug helpers.
- Initializes/resets/shuts down all devices through `devtab`.
- Implements mount and unmount mechanics with `Mhead` and `Mount` chains, including replacement and union mount ordering.
- Resolves paths with `walk()`, handling mount traversal, union fallback, dot-dot across mounts, and partial walk errors.
- Implements `namec()` for Plan 9 access modes: access, bind, to-directory, open, mount, create, and remove.
- Handles create races by retrying as open-with-truncation when non-exclusive create fails after another creator wins.
- Parses and cleans path names, validates invalid characters/control bytes, and enforces noattach sandbox exceptions.
- Provides helpers such as `cunique`, `eqchan`, `findmount`, `domount`, `undomount`, `createdir`, `putmhead`, `validname`, and `isdir`.

Important behavior:
- Device names beginning with `#` bypass normal mounts and attach directly to `devtab` entries.
- `namec(Aopen)` and `namec(Acreate)` ensure callers get a unique channel suitable for mutation by device open/create/remove.
- Union mounts are searched when a walk fails in the first mounted element.
- Cnames are updated alongside successful walks to preserve printable path state.

Dependencies:
- Heavily depends on `dat.h` structures, device method tables, process-global `up`, mount locks, `fcall` stat conversion, and Plan 9 error unwinding.

Notable risks:
- Code is subtle and retains diagnostic prints for unexpected `umh` states.
- Some comments call out unresolved race semantics and historical complexity around union/create behavior.
- `putmhead()` poisons the mount pointer with `0xCafeBeef` on final release for diagnostics.
