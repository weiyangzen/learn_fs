# File Research: sources/os/linux/linux/fs/ocfs2/ocfs2_lockingver.h

Role: Defines the OCFS2 cluster locking protocol version.

Key contents:
- `OCFS2_LOCKING_PROTOCOL_MAJOR` is `1`.
- `OCFS2_LOCKING_PROTOCOL_MINOR` is `0`.
- Comment records version `1.0` as the initial locking version from OCFS2 1.4 and points readers to `dlmglue.c` for protocol details.

Design notes:
- This small header centralizes protocol version constants used when validating cluster locking compatibility.
