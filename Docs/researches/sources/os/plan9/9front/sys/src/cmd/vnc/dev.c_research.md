# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/dev.c

## Role

`dev.c` implements common Plan 9 device helper routines for the user-space VNC server device filesystem.

## Main Behavior

- `mkqid()` fills `Qid` fields.
- `devno()` maps device character identifiers to entries in `devtab`.
- `devdir()` and `devgen()` build directory entries from `Dirtab` records.
- `devattach()` creates a root channel for a device.
- `devclone()` copies channel metadata for walk operations.
- `devwalk()` implements generic walking through static/generated device directory entries.
- `devstat()` and `devdirread()` implement generic stat and directory read operations.
- `devpermcheck()` and `devopen()` enforce simple owner/eve/other permissions and open-mode constraints.
- Default create, remove, wstat, block read, and block write handlers reject unsupported operations.

## Notable Limitations And Risk Areas

- Permission checking is simplified around `up->user` and `eve`.
- `devdirread()` uses variable-length `convD2M()` entries and returns `-1` when the caller buffer cannot hold the first entry.
- Device-specific generators must follow the expected `-1`, `0`, `1` convention.
- `devwalk()` can return partial walks with no cloned channel, matching 9P walk semantics.
