# File Research: sources/os/bsd/freebsd-src/sbin/bectl/bectl_jail.c

## Purpose
Implements `bectl jail` and `bectl unjail` support: mounting a boot environment, creating a jail rooted there, optionally running a command, and cleaning up.

## Main Elements
- Jail parameter management:
  - `jailparam_add()`, `jailparam_del()`, `jailparam_addarg()`, `jailparam_delarg()`.
  - Blocks dangerous caller-supplied jail params including `command`, `exec.start`, `persist`, and `nopersist`.
- `build_jailcmd()`: constructs `/usr/sbin/jail -c` argv from nvlist params and optional command, defaulting interactive mode to `/bin/sh`.
- `bectl_cmd_jail()`: parses `-b`, `-o`, `-U`, `-u`; mounts the BE; sets default hostname/path; forks and execs `jail`; optionally removes jail and unmounts BE.
- `bectl_jail_cleanup()`: removes jail and unmounts non-ZFS filesystems beneath the BE path.
- `bectl_search_jail_paths()` / `bectl_locate_jail()`: find jails by jid/name or by matching mounted BE path.
- `bectl_cmd_unjail()`: locates jail, verifies its path belongs to a mounted BE, removes jail, and unmounts.

## Dependencies And Integration
Uses libjail, `jail_getv()`, `jail_getid()`, `jail_remove()`, filesystem mount table inspection, and libbe mount state.

## Risk Notes
Cleanup walks mountpoints beneath the BE path and unmounts non-ZFS filesystems. Jail parameter filtering prevents callers from overriding command/persist semantics that would break lifecycle control.
