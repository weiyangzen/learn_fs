# File Research: sources/local-fs/e2fsprogs/misc/fsck.c

## Purpose
Implements generic `fsck`, a parallelizing dispatcher for filesystem-specific checkers.

## Key Elements
Loads filesystem entries from `FSTAB_FILE` or `/etc/fstab`, parsing escaped fields and resolving labels/UUIDs through blkid. Tracks entries as `struct fs_info` and child checker processes as `struct fsck_instance`.

Parses fsck options, including `-A`, `-C`, `-M`, `-N`, `-P`, `-R`, `-T`, `-V`, `-s`, `-t`, `--`, and device arguments. Compiles `-t` filters into normal type matches and `opts=` option filters, including historical `loop` handling.

Finds checker binaries along built-in fsck paths plus `PATH`, spawns `fsck.<type>` children, manages progress ownership for ext-family checkers via `-C` and `SIGUSR1`, and waits/ORs exit statuses. `check_all` handles pass-number ordering, root-first behavior, mounted-skip mode, same-base-device serialization, `FSCK_FORCE_ALL_PARALLEL`, and `FSCK_MAX_INST`.

## Dependencies
Uses blkid, e2fsprogs support helpers `get_devname` and `base_device`, NLS/com_err setup, `is_mounted`, POSIX fork/exec/wait/signal APIs, and filesystem checker executables.

## Behavior/Risks
Uses fixed `MAX_DEVICES` and `MAX_ARGS` arrays. Parallelism is conservative unless forced, but base-device detection is heuristic and unknown devices serialize. Cancellation sends SIGTERM to outstanding children. The option parser is hand-written, so fs-specific option forwarding remains intentionally simple.
