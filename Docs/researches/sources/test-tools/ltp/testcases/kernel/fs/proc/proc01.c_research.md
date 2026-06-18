# sources/test-tools/ltp/testcases/kernel/fs/proc/proc01.c

## Purpose

`proc01.c` recursively opens and reads regular files under `/proc` to catch kernel procfs read bugs while filtering known expected failures and dangerous paths.

## Important APIs, Types, and Functions

Important functions are `found_errno`, `setup`, `cleanup`, `help`, `readproc`, and `main`. Options control read buffer size, per-file byte limit, whether to read `/proc/irq`, root proc path, and verbose mode. Static tables define known open/read errno mappings, SELinux paths expected to work, and paths that ignore `O_NONBLOCK`.

## Control Flow

`main` parses options, validates buffer and max byte settings, sets `procpath`, and loops through `readproc`. `readproc` `lstat`s each object, avoids symlink loops except `/proc/self`, recursively descends directories while skipping `kcore`, numeric pids under top `/proc`, and `/proc/irq` unless requested, then opens regular files with `O_NONBLOCK` and reads until EOF, max bytes, or a filtered error.

## State and Persistence Behavior

No persistent filesystem state is created beyond the LTP temporary directory. Global counters `total_read` and `total_obj` accumulate across calls and loops. A static read buffer of up to 64 KiB is reused.

## Dependencies and Integration Points

Uses legacy LTP, procfs, `fnmatch`, `dirent`, `open`/`read`, optional libselinux `is_selinux_enabled`, and known kernel/LSM path behavior.

## Risks and Edge Cases

The list of known failures is kernel-version-sensitive. Some proc files may block despite `O_NONBLOCK`, so `error_nonblock` must be maintained. Counters are not reset per loop. `atoi` option parsing accepts malformed suffixes.

## Test Signals

Pass is `readproc() completed successfully` with total bytes and object count. `TFAIL` reports unexpected `lstat`, `opendir`, `open`, or `read` errors; known issues are logged as `TINFO`.
