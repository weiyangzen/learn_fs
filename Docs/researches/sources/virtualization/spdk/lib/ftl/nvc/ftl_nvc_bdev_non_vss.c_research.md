# File Research: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_bdev_non_vss.c

Implements an NV cache backend for bdevs without separate metadata/VSS.

Important behavior:
- Accepts only bdevs with metadata size `0`.
- Initializes/deinitializes P2L log support.
- On chunk open, acquires a P2L log tied to chunk sequence ID; on close, releases it.
- Writes user IO with `spdk_bdev_writev_blocks()`, then logs P2L entries before completing the NV cache write.
- Recovers open chunks by reading P2L logs and rebuilding chunk address mappings.
- Creates and opens P2L log IO layout regions during setup.

Risk:
- `init()` ignores nonzero `ftl_p2l_log_init()` return and still returns `0`, which may hide initialization failure.
