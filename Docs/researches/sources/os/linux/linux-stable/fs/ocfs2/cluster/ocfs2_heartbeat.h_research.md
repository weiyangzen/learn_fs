# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/ocfs2_heartbeat.h

## Summary
Defines the on-disk heartbeat block layout shared by kernel heartbeat code and userspace-facing OCFS2 cluster tooling.

## Main Responsibilities
- Define `struct o2hb_disk_heartbeat_block`.
- Store heartbeat sequence, node number, CRC checksum, generation, and dead timeout in disk-endian fields.

## Key Interfaces
- `hb_seq` is the changing heartbeat value.
- `hb_node` records the node slot owner.
- `hb_cksum` protects the block.
- `hb_generation` distinguishes node restart/rejoin cycles.
- `hb_dead_ms` advertises the node’s dead timeout expectation.

## Risks
This is an on-disk ABI. Field layout or size changes would affect compatibility with existing heartbeat regions and tooling.
