# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/all.h

Top-level include and shared global declaration header for cwfs.

It includes Plan 9 system headers, disk/network/auth-facing headers, `dat.h`, and `portfns.h`, redirects `malloc` to `ialloc`, defines common macros and time helpers, declares qid/permission constants, and exposes major global state: users/groups, file tables, channels, locks, queues, devices, config flags, service name, filesystems, and error strings.

This is the common glue included by cwfs protocol, auth, check, and configuration modules.
