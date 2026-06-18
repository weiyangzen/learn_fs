# File Research: sources/virtualization/virtiofsd/src/main.rs

## Scope

Daemon entrypoint and command-line runtime setup for virtiofsd.

## APIs And Configuration

- Defines `Opt` with clap options for shared directory, socket/fd, socket group, thread pool, xattrs, POSIX ACLs, xattr maps, sandbox, readonly, seccomp, submount announcement, inode file-handle mode, cache policy, mmap/direct I/O/writeback, compatibility flags, logging, rlimits, namespace ID maps, soft ID translation, noatime handling, and migration behavior.
- Parses seccomp action, vhost-user tag, inode file-handle modes, legacy `-o` options, and capability modification strings.
- `run_generic_fs()` builds and runs `VhostUserDaemon`.

## Behavior

- `--print-capabilities` emits JSON with `migrate-precopy` and `separate-options`.
- Validates shared directory existence and migration option compatibility.
- Computes cache timeout and readdirplus policy from cache options.
- Creates or adopts a vhost-user listener, writes a socket pid file, applies socket permissions/group, and raises `RLIMIT_NOFILE`.
- Computes guest FD quota after reserving internal FDs for memory slots and worker threads.
- Enters configured sandbox before building passthrough config.
- Enables seccomp before starting worker threads.
- Drops Linux capabilities when running as root, with `DAC_READ_SEARCH` required for file-handle inode mode.
- Chooses read-only or normal passthrough filesystem and starts the vhost-user backend.

## Risks And Invariants

- Many options are compatibility-sensitive with older QEMU/legacy virtiofsd syntax.
- Seccomp must be installed before thread-pool creation.
- Sandbox entry changes process view of paths and descriptors, so config captures required proc/mountinfo FDs.
- Migration mode flags are rejected when semantically incompatible.
