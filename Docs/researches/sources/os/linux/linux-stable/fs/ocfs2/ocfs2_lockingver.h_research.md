# File Research: sources/os/linux/linux-stable/fs/ocfs2/ocfs2_lockingver.h

Purpose: defines the OCFS2 cluster locking protocol version.

Read coverage: complete file read, 22 lines.

Key contents:
- Declares locking protocol major version `1` and minor version `0`.
- Comments identify this as the initial OCFS2 1.4 locking version and point readers to `dlmglue.c` for protocol details.

Dependencies:
- Used by cluster stack/DLM compatibility checks so nodes agree on the lock protocol before sharing a volume.

Risk and edge cases:
- Version values are cluster-compatibility gates; changing them requires corresponding protocol negotiation and compatibility handling in DLM glue.
