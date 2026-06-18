# sources/user-network-fs/samba/source3/torture/proto.h

## Purpose
`proto.h` is the source3 SMB torture harness declaration header. It exposes test entry points and helper APIs across the many `source3/torture` compilation units.

## Important APIs, types, and functions
The header includes `source3/include/client.h` and `source3/libsmb/proto.h`, then declares denial tests, mangle test, `nbio` primitives, scanner entry points, connection helpers from `torture.c`, low-level SMB helper wrappers, Unicode/case table tests, POSIX tests, SMB2/DFS/notify/dbwrap/messaging/g_lock/idmap/cache tests, and local regression tests such as `run_local_conv_auth_info`.

## Control flow
There is no executable control flow in the header. Its declarations let `torture.c` build a registry of named test operations and let individual files call shared connection, cleanup, and raw-SMB helpers.

## State and persistence behavior
The header owns no state. It exposes functions that operate on `cli_state` connections and remote test shares, and it makes dependencies on globals in `torture.c` visible indirectly through implementation files.

## Dependencies and integration points
Every file in this work item except standalone binaries uses or is represented by this header. The declared functions are wired into the `smbtorture3` binary via `wscript_build` and the `torture_ops[]` registry in `torture.c`.

## Risks and test signals
Because this is a broad manual prototype header, stale declarations can cause build failures or hide ownership boundaries between torture modules. It is a useful integration map: functions declared here are expected to be callable by the harness and should remain source3-client compatible.
