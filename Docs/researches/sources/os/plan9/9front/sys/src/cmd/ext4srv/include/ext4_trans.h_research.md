# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_trans.h

Transaction wrapper API header for metadata block access and dirty/revoke operations.

Key behavior:
- Declares `ext4_trans_set_block_dirty` for routing dirty buffers into the active transaction or cache.
- Declares transaction-aware cached block get functions with and without read.
- Declares `ext4_trans_try_revoke_block` for revoking or flushing a logical block address.

Notable dependencies:
- Includes `ext4_config.h` and `ext4_types.h`.
- Implemented by `ext4_trans.c`.

Research notes:
- The comments mention write-access acquisition, but the implementation currently only delegates block fetches and handles dirty/revoke semantics.
