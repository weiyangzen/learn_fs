## sources/user-network-fs/nfs-utils/utils/nfsdctl/nfsdctl.h

Purpose: Provides generated NFSv4 compound operation numbers used by `nfsdctl.c` to label server RPC status data.

Important APIs/types/functions: Defines `enum nfs_opnum4`, covering core NFSv4.0 operations, NFSv4.1 session/pNFS operations, NFSv4.2 operations, xattr operations, and `OP_ILLEGAL`.

Control flow: No executable flow; consumers index operation-name tables with enum constants received from kernel netlink status attributes.

State and persistence: No state or persistence. Its correctness depends on staying synchronized with `Documentation/netlink/specs/nfsd.yaml` and kernel UAPI expectations.

Dependencies and integration: Included by `nfsdctl.c`; paired with generated or system nfsd netlink headers. The SPDX line allows GPL syscall-note or BSD-3-Clause use.

Risks and test signals: Drift between enum values and kernel attributes would mislabel RPC operations. Tests should compare values against the generated kernel header/spec and check bounds for sparse/unknown op numbers.
