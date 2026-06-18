# File Research: sources/local-fs/btrfs-progs/cmds/scrub.c

## Purpose

Implements the `btrfs scrub` command group: start, resume, cancel, status, and per-device throughput limit management. It wraps kernel scrub ioctls, maintains persistent scrub status files, exposes live progress through a Unix socket, and formats per-device or filesystem-wide reports.

## Commands

- `scrub start`: starts scrub, optionally foreground/background, read-only, raw/per-device output, ioprio, force, and throughput limit.
- `scrub resume`: resumes canceled/interrupted scrub from recorded `last_physical`.
- `scrub cancel`: issues `BTRFS_IOC_SCRUB_CANCEL`.
- `scrub status`: reads live socket or persisted status file and prints progress/history.
- `scrub limit`: shows or writes `devinfo/<devid>/scrub_speed_max` sysfs limits.

## Core Data Structures

- `struct scrub_progress`: per-device ioctl args, fd, status, old/new limits, ioprio, mutex, and resume pointer.
- `struct scrub_file_record`: persisted status for one fsid/devid.
- `struct scrub_progress_cycle`: progress-thread context for periodic ioctl polling, socket service, and status writes.
- `struct scrub_fs_stat`: aggregate filesystem stats for summary output.

## Control Flow

1. `scrub_start()` opens the mount, gets filesystem/device info, reads prior status, checks whether scrub is already running, and prepares per-device progress records.
2. It optionally creates a progress socket and initial status file.
3. In background mode it forks; the child starts per-device scrub threads and one progress thread.
4. `scrub_one_dev()` calls `BTRFS_IOC_SCRUB`; `scrub_progress_cycle()` polls `BTRFS_IOC_SCRUB_PROGRESS`, writes status, and serves socket clients.
5. On completion it restores device limits, joins threads, records final status, prints summaries if requested, and returns special statuses for no resume or uncorrectable errors.

## Status File Format

- Stored under `/var/lib/btrfs/scrub.status.<fsid>`.
- Versioned with `scrub status:1`.
- Parser `scrub_read_file()` is a state machine that reads fsid/devid and key-value progress/stat fields.
- Writer `scrub_write_file()` serializes the same fields through helper macros.

## Dependencies

Uses Btrfs scrub ioctls, fs/device info helpers, sysfs utilities, units formatting, string tables, pthreads, signals, Unix sockets, flocked status files, and UUID utilities.

## Risks And Edge Cases

- The status parser is hand-written and stateful; malformed files are skipped/reported, but parser complexity is high.
- Thread cancellation is asynchronous in the progress thread, requiring careful mutex and file-write cancellation protection.
- Background mode relies on status files and socket cleanup; stale sockets are detected and unlinked when connection is refused.
- `scrub_write_file()` contains a suspicious call sequence around writing the devid: after `scrub_writev()` it calls `scrub_write_buf(fd, buf, ret)`, where `ret` is not clearly the formatted byte count at that point.
- Limit handling writes sysfs values before scrub and attempts to restore old values later; failures are warnings, so limits can remain changed if reset fails.
