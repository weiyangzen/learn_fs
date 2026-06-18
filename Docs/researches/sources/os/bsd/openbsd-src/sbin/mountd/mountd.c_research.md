# File Research: sources/os/bsd/openbsd-src/sbin/mountd/mountd.c

Purpose: Implements OpenBSD `mountd`, the NFS mount protocol daemon. It parses `/etc/exports`, maintains an in-memory export tree and remote mount list, registers RPC mount services for v1/v3 over UDP/TCP, and coordinates kernel export updates.

Process model:
- `main()` parses `-d`, optional exports file path, daemonizes unless debugging, writes `/var/run/mountd.pid`, creates an `AF_UNIX` socketpair, and forks a privileged child.
- Parent pledges `stdio rpath inet dns getpw`, parses export state, loads `/var/db/mountdtab`, registers `RPCPROG_MNT` v1/v3, then runs `mountd_svc_run()`.
- Child `privchild()` unveils `/` read-only and `/var/db/mountdtab` read/write/create, then services `imsg` requests that require retained privilege.

Privilege separation:
- Parent requests privileged operations through `imsg`: `getfh()`, kernel export changes through `mount(..., MNT_UPDATE, export_args)`, deleting exports, and appending/rewriting the remote mount table.
- `imsg_getfh()` and `imsg_export()` validate response message type and size before using returned data.
- Child validates message sizes and mount-list strings before file writes, though mount-list writes are deliberately simple append/rewrite operations.

Export parsing:
- `get_exportlist()` frees previous export/group state, gathers local mount table entries, sends pending de-export requests for stale exportable filesystems, opens the exports file, and parses one logical line at a time.
- Directory fields must appear before options/hosts. `check_dirpath()` rejects paths with symlink or non-directory/non-regular components.
- Options include `ro`, `maproot`/`root`, `mapall`, `mask`, `network`, and `alldirs`; `check_options()` enforces consistency such as `-mask` requiring `-network` and `-mapall` excluding `-maproot`.
- Host entries may be DNS names, numeric IPv4 addresses, networks, or netgroups. Duplicate hosts on a line are ignored.

Export data structures:
- `exportlist` groups exports by filesystem id and stores a directory tree plus optional `-alldirs` default directory.
- `dirlist` is a binary tree ordered by exported path and carries default/host flags and host lists.
- `grouplist` represents individual host or network selectors; `hostlist` links them to directories.
- `hang_dirp()`, `add_dlist()`, `dirp_search()`, `chk_host()`, and `scan_tree()` implement lookup and authorization matching.

RPC behavior:
- `mntsrv()` handles `NULLPROC`, `MOUNT`, `DUMP`, `UMOUNT`, `UMNTALL`, and `EXPORT`.
- Mount requests from unreserved ports are rejected. Paths are canonicalized with `realpath()`, checked against export rules, and converted to file handles through the privileged child.
- Successful mounts are recorded in memory and appended to `/var/db/mountdtab`; unmount calls remove matching host/path entries.
- `xdr_fhs()`, `xdr_mlist()`, and `xdr_explist()` encode mount protocol replies.

Mount list persistence:
- `get_mountlist()` loads `/var/db/mountdtab`.
- `add_mlist()` deduplicates host/path pairs then asks the child to append.
- `del_mlist()` removes entries in memory and asks the child to rewrite the full file through open/write/close imsgs.

Signals and shutdown:
- `SIGCHLD`, `SIGHUP`, and `SIGTERM` set flags only.
- The service loop reaps child exit, reloads exports on HUP, and on termination broadcasts `RPCMNT_UMNTALL` before exit.
