# File Research: sources/local-fs/ocfs2-tools/include/o2cb/ocfs2_nodemanager.h

This header defines userspace-visible constants for the OCFS2 nodemanager kernel interface.

Key content:
- `O2NM_API_VERSION = 5`
- Maximum nodes: 255
- Invalid node number: 255
- Maximum name length: 64
- Maximum global heartbeat regions: 32, with warning that changing it breaks DLM compatibility.

Integration notes:
- Pure constants header; included by `o2cb.h`.
