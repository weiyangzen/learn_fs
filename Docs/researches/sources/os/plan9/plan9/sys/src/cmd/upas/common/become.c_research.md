# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/common/become.c

- Role: Drops process identity/namespace to a powerless user.
- Key function: `become(cmd, who)` supports `who == "none"` by writing `none` to `#c/user` and installing a new namespace with `newns`.
- Integration: Called by process spawning helpers when a child should run as another user.
- Risks/notes: Only implements special handling for `none`; other names return success without changing identity.
