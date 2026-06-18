# sources/user-network-fs/libfuse/util/mount.fuse.c

## Purpose
`mount.fuse3` helper used by mount(8)/fstab style invocations. It parses source/type/options, optionally uses service-mount support, can pass an already opened FUSE fd, can drop privileges before executing the filesystem binary, and finally execs the FUSE filesystem command through `/bin/sh`.

## Important APIs, Types, And Functions
- `prepare_fuse_fd` opens a libfuse channel and clears `FD_CLOEXEC` so the filesystem process can inherit it.
- Linux capability helpers `get_capabilities`, `set_capabilities`, and `drop_and_lock_capabilities` support `drop_privileges`.
- `check_binary_access` verifies executable availability after privilege drop.
- Service mount helpers `mount_service_child` and `try_service_main` prefer `fuservicemount3` when available and compatible.
- `add_arg` shell-quotes command arguments.

## Control Flow
The program derives filesystem type from its argv[0], `-t`, or `type#source`. It filters mount options, ignoring fstab-only options and recognizing `setuid=`, `drop_privileges`, `dev/nodev`, and `suid/nosuid`. It may switch uid/gid, prepare an inherited FUSE fd, drop and lock capabilities, try service-mount unless incompatible, then builds a shell command from type/source/mountpoint/options and `execl`s `/bin/sh -c`.

## State And Persistence
Persistent effects are delegated to the filesystem command or service mount. Process state changes can include uid/gid switch, securebits, capability bounding-set drops, no_new_privs, inherited FUSE fd, and `HOME=/root` defaulting for boot environments.

## Dependencies And Integration Points
Called by mount utilities. Uses libfuse `fuse_open_channel`, optional `mount_service` APIs, Linux capability syscalls, passwd database, and `/bin/sh`.

## Risks
The final shell execution path is sensitive, though `add_arg` single-quotes arguments. `drop_privileges` requires `CAP_SYS_ADMIN` and `CAP_SETPCAP` and permanently prevents privilege regain. Service mount is skipped when a preopened fd or setuid target is requested. Clearing `FD_CLOEXEC` is deliberate but should be constrained to the intended fd.

## Test Signals
Test `type#source` parsing, argv[0]-derived types, ignored fstab options, setuid success/failure, drop_privileges capability requirements, shell quoting with quotes/spaces, pass_fuse_fd inheritance, service mount fallback, and executable lookup after dropping privileges.
