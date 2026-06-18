# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_recv.h

Read status: complete, 71 lines.

Purpose: receive-side DMU send stream interface.

Key structures and APIs:
- `recv_clone_name` extern identifies clone receive naming support.
- `dmu_recv_cookie_t` carries receive state: target dataset/snapshot names, begin record pointers, flags for newfs/byteswap/force/resumable/raw/clone/spill, GUID map, raw key nvlist, checksum, snapshot object ids, IV-set GUID, owner, and credential.
- `dmu_recv_begin()` validates/prepares a receive.
- `dmu_recv_stream()` consumes stream data from a vnode/offset and supports cleanup/action handle plumbing.
- `dmu_recv_end()` finalizes receive state.
- `dmu_objset_is_receiving()` tests whether an objset is in receive mode.

Dependencies: integer types, DSL crypto, SPA, vnode, nvlist, credentials, replay record forward declarations.

Research notes:
- Supports resumable and raw encrypted receives through cookie fields and crypto nvlist handling.
