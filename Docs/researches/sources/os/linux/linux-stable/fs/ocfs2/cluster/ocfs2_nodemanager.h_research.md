# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/ocfs2_nodemanager.h

## Summary
Defines userspace/kernel constants for the OCFS2 nodemanager interface.

## Main Responsibilities
- Publish nodemanager API version.
- Define maximum node count and invalid node number.
- Define maximum cluster/node/host name length.
- Define maximum global heartbeat regions.

## Key Interfaces
- `O2NM_API_VERSION` is exposed through `/sys/fs/o2cb/interface_revision`.
- `O2NM_MAX_NODES` and `O2NM_INVALID_NODE_NUM` are both 255.
- `O2NM_MAX_REGIONS` is 32 and documented as DLM compatibility-sensitive.

## Risks
These constants form ABI and protocol limits. Changing max regions or node numbering can break DLM and userspace compatibility.
