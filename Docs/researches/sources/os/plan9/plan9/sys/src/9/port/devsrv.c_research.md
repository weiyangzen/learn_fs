# File Research: sources/os/plan9/plan9/sys/src/9/port/devsrv.c

Purpose: Service registry device `#s`. It lets processes post already-open file descriptors under names so other processes can open those names and receive the underlying channel.

Key logic:
- `create` creates a named service entry and assigns an incrementing qid path.
- `write` to the newly created file parses an fd number, obtains the channel with `fdtochan`, rejects close-on-exec/remove-on-close and auth files, and stores it.
- `open` of an existing service replaces the lookup channel with the posted channel after permission and mode checks.
- `remove` unlinks service entries with special restrictions for `eve`-owned services and `boot`.
- `wstat` allows owner/eve to change permission, owner, and name.

Dependencies and integration:
- Uses Plan 9 `Chan` reference counting, `fdtochan`, `devwalk/devstat`, qid generation, and service lookup helper `srvname`.

Risks and notes:
- Posted channel mode must match requested open mode unless the posted channel is `ORDWR`.
- Service entries exist before a channel is posted; opening an unposted service returns shutdown.
- Removal rules protect system services more strongly than personal services.
