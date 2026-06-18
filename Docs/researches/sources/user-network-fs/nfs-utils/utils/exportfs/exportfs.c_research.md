<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/exportfs/exportfs.c -->
# sources/user-network-fs/nfs-utils/utils/exportfs/exportfs.c

## Purpose
`exportfs` is the administrative CLI for listing, exporting, unexporting, reexporting, validating, and flushing NFS exports. It reads `/etc/exports` and exports.d data, updates the etab state file, and notifies kernel/user-space caches.

## APIs And Control Flow
`main` parses `-a`, `-r`, `-u`, `-o`, `-i`, `-f`, `-L`, `-v`, and `-s`, validates incompatible modes, initializes state paths and nfsd paths, serializes writers with `grab_lockfile`, reads configured exports unless ignored, marks all exports or parses explicit `host:/path` arguments, writes etab, flushes caches, and frees export state. `exportfs_parsed` creates or updates an export entry and calls `validate_export`. IPv6 bracket syntax is handled separately. `unexportfs_parsed` clears active flags and, when possible, sends an NFSD netlink unlock-export command if no export remains for a path. `dump` renders current exports in table or exports-file format.

## State, Dependencies, And Integration
State includes the lock fd, `f_unexport_all`, global `no_netlink`, `exportlist`, etab paths, cache channels, DNS resolution, and optional NFSD/SUNRPC generic netlink. It integrates support/export parsing, xtab/etab persistence, reexport options, secinfo/xprtsec display, and kernel export validation.

## Risks And Test Signals
Risks include in-place mutation of argv strings while parsing, DNS dependence for hostname matching, best-effort lock failure logging, time-2038 handling for proc cache probes, netlink/proc fallback differences, and validation warnings that do not fail the command. Test list/export/unexport/reexport modes, IPv6 host syntax, trailing slash unexport, wildcard/netgroup names, invalid options, netlink unlock failures, and concurrent writers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/exportfs/exportfs.c -->
