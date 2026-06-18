# File Research: sources/os/bsd/dragonflybsd/sys/sys/syslink_rpc.h

Minimal syslink RPC descriptor definitions.

Key contents:
- Defines `struct syslink_desc`:
  - `sd_offset`: offset into an operations structure
  - `sd_name`: debug name

Role:
- Supports syslink protocol abstraction for RPC operations.
- The comment notes this descriptor is also used by vnode operations and device operations.

Research notes:
- This is a small shared metadata contract rather than a full RPC implementation.
- Offset-based descriptors allow generic dispatch/conversion logic to identify operation slots.
