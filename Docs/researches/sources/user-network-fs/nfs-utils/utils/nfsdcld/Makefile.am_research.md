<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/Makefile.am -->
# sources/user-network-fs/nfs-utils/utils/nfsdcld/Makefile.am

## Purpose

`nfsdcld/Makefile.am` builds the `nfsdcld` NFSv4 client-tracking daemon.

## Important APIs, types, and functions

It builds `nfsdcld` from `nfsdcld.c`, `sqlite.c`, and `legacy.c`; installs `nfsdcld.man`; defines `_LARGEFILE64_SOURCE`; declares internal headers; and links support NFS, libevent, sqlite, and libcap.

## Control flow

Automake turns these declarations into compile/link/install rules. There are no custom install rename hooks in this file.

## State and persistence behavior

No runtime state is managed by the Makefile. The linked daemon manages SQLite and legacy recovery directories at runtime.

## Dependencies and integration points

The link dependencies reflect runtime behavior: libevent for pipe events, sqlite for persistent tracking, libcap for capability dropping, and support NFS for shared constants/helpers.

## Risks and edge cases

Builds without the expected libevent/sqlite/libcap flags will fail. `_LARGEFILE64_SOURCE` must match any file-offset assumptions in sqlite or system headers.

## Test signals

Build tests should verify daemon linking with and without capability headers and that generated distribution archives include the manpage and internal headers as expected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/Makefile.am -->
