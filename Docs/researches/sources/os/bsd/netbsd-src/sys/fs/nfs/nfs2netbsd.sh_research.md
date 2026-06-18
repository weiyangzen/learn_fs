# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/nfs2netbsd.sh

This shell script is an import helper for arranging FreeBSD's new NFS source tree into NetBSD's `sys/fs/nfs` layout. It copies selected FreeBSD files, rewrites source-identification tags, moves old and new NFS headers to avoid collisions, rearranges directories, generates a starter `files.newnfs`, and prints the CVS import command to run afterward.

Key steps:
- Validates that exactly one argument is supplied and that it names a FreeBSD `sys` directory.
- Extracts file paths from FreeBSD `conf/files` entries containing `nfscl` or `nfsd`, excluding `rpc/` and `xdr/`.
- Finds additional headers under the selected directories and adds them to the copy list.
- Creates the destination directory hierarchy.
- Copies files with an `awk` filter that strips dollar signs from FreeBSD/NetBSD RCS tags, comments out imported NetBSD/FreeBSD ID macros as needed, and injects a fresh NetBSD tag.
- Renames old `nfs/nfsproto.h` to `nfs/oldnfsproto.h` and old `nfs/xdr_subs.h` to `nfs/old_xdr_subs.h`.
- Checks for filename collisions between `nfs/` and `fs/nfs/` before merging.
- Moves old `nfs` and common `fs/nfs` files into `fs/nfs/common`, renames `fs/nfsserver` to `fs/nfs/server`, `fs/nfsclient` to `fs/nfs/client`, and `nlm` to `fs/nfs/nlm`.
- Generates `fs/nfs/files.newnfs` by translating FreeBSD config tokens such as `nfscl`, `nfsd`, `nfslockd`, `nfs_root`, `bootp`, and `inet` into NetBSD config expressions.
- Moves the staged `fs/nfs/*` contents into the current directory and removes temporary directories.

Important behavior:
- The script expects to run in an empty current directory and copies from an external FreeBSD source tree rather than transforming files in place.
- Section 4 directory rearrangements and section 5 `files.newnfs` path rewrites must stay in sync.
- Generated `files.newnfs` is explicitly described as a starting point, not a finished kernel config file.

Research notes:
- This file explains why the NetBSD tree contains imported FreeBSD layout/provenance markers and renamed `old*` protocol/XDR headers.
- If updating from a newer FreeBSD newnfs tree, collision handling and token translation are the main maintenance points.
