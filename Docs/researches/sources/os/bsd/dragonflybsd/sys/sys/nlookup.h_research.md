# File Research: sources/os/bsd/dragonflybsd/sys/sys/nlookup.h

DragonFlyBSD namecache-based path lookup state and API.

Key responsibilities:
- Defines `struct nlcomponent` for a path component pointer and length.
- Defines `struct nlookupdata`, which encapsulates lookup result, base/root/jail namecache handles, path buffer, thread, credentials, directory vnode, flags, symlink loop count, directory error, iteration number, and `vn_open()` result state.
- Defines nlookup flags controlling symlink following, mount crossing, buffer ownership, whiteout/directory state, locks, open/create/delete/rename/truncate/hardlink checks, NFS behavior, shared locking, access bits, credential borrowing, sticky/append-only/immutable/writable indicators, and vnode return behavior.
- Defines masks for all permission checks and modifying operations.
- Declares kernel nlookup initialization, cleanup, path walk, simple lookup, mount lookup, symlink read, zeroing, and access-check APIs.

Important behavior:
- `nl_op`-style operation semantics are replaced by flags; operation bits are used for access checks and do not themselves modify the returned namecache.
- `vn_open()` may populate `nl_open_vp`, and `nlookup_done()` will close it unless the caller extracts and nulls it.
- `NLC_HASBUF` marks path buffer ownership.
- `NLC_BORROWCRED` marks borrowed credential references.

Dependencies:
- Includes `namecache.h` and `file.h`.
- Kernel section includes `_uio.h` and uses vnodes, mounts, credentials, threads, and attributes.

Notable risks:
- Cleanup ownership is easy to get wrong, especially for `nl_path`, `nl_cred`, `nl_dvp`, and `nl_open_vp`.
- Access-check flags and modifying-operation flags are separate from actual mutation; callers must use `vn_open()`/VOPs for changes.
- Symlink loop handling depends on `nl_loopcnt`.
