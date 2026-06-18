<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/nfsdcld.c -->
# sources/user-network-fs/nfs-utils/utils/nfsdcld/nfsdcld.c

## Purpose

`nfsdcld.c` implements the long-running NFSv4 client-tracking daemon that communicates with the kernel over the nfsd cld pipe, persists client IDs in SQLite, sends recovery records during grace, and handles first-time migration from older trackers.

## Important APIs, types, and functions

Key helpers include `cld_set_caps`, `cld_pipe_open`, `cld_inotify_setup`, `cld_pipe_init`, `cld_check_grace_period`, `cld_message_size`, command handlers `cld_create`, `cld_remove`, `cld_check`, `cld_gracedone`, `cld_gracestart`, `cld_get_version`, `cld_not_implemented`, `cld_pipe_read_msg`, and event callback `cldcb`. `main` handles config, daemonization, capability dropping, database setup, pipe event registration, signals, and cleanup.

## Control flow

Startup reads `nfs.conf`, accepts foreground/debug/pipefs/storage options, builds `<pipefs>/nfsd/cld`, daemonizes unless foreground, drops all capabilities, checks storage writability, flags old kernels before 4.20, opens/prepares SQLite, installs inotify for the pipe directory, opens the cld pipe if present, and enters libevent dispatch. Pipe events read a message header and body, switch on command, update SQLite or iterate recovery records, write a downcall response, and re-add the event. If the pipe disappears or writes fail, the daemon reopens it.

## State and persistence behavior

Persistent state is `main.sqlite` under the storage directory, with current/recovery epoch tables and migration parameters. Runtime state includes pipe fd/event, inotify fd/event, signal state, and epoch globals. First-time grace completion can delete old cltrack records and clear legacy recovery directories before marking `first_time=0`.

## Dependencies and integration points

It depends on libevent, inotify, libcap, `cld.h` kernel upcall formats, procfs `v4_end_grace` for old kernels, SQLite backend, legacy migration helpers, config parsing, and `version.h`. It integrates with the kernel through rpc_pipefs and with older tracking mechanisms through migration.

## Risks and edge cases

Message size handling exits fatally on unknown versions. V2 create stores principal hashes, but remove/check use the v1 name field, so kernel message layout compatibility is critical. Old-kernel grace detection reads a single proc byte and synthesizes `sqlite_grace_start`. Many pipe write failures trigger reopen but not command replay. Capability dropping can make storage misownership fatal later.

## Test signals

Tests should cover v1/v2 upcalls, create/remove/check/gracestart/gracedone/getversion, pipe absent then created, pipe reopen after write failure, unsupported command response, old-kernel grace detection, first-time migration cleanup, storage permission warnings, signal shutdown, and recovery iteration with principal hashes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/nfsdcld.c -->
