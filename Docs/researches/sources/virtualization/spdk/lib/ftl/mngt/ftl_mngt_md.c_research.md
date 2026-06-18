# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_md.c

Management helpers for layout setup, metadata object creation/destruction, metadata persist/restore, superblock initialization/validation, and clean/fast shutdown metadata flows.

Key flows:
- `ftl_mngt_init_layout` calls `ftl_layout_setup`.
- `ftl_mngt_init_md` creates `ftl_md` objects for all active layout regions, skips already-created superblock objects, and aliases mirror metadata buffers for no-buffer mirror regions.
- Persist helpers serialize NV-cache state, valid map, P2L checkpoints, band metadata, trim metadata, and superblock.
- Fast persist only saves NV-cache state and relies on shared memory for most metadata.
- Superblock CRC is computed excluding the CRC field, with legacy v2 special sizing.
- Default superblock initialization sets magic/version/UUID/clean flags, max relocation queue depth, overprovisioning, device type names, invalid layout blob IDs, and CRC.
- Superblock restore validates magic, CRC, upgrade compatibility, UUID, LBA count, overprovisioning, and blob area.
- Superblock management creates SHM metadata, lays out/mirrors SB regions, handles retry with new SHM, and runs init or restore sub-processes.
- Restore metadata supports fast startup from SHM or normal disk restore for NV-cache, valid map, band metadata, and trim metadata.

Role: this is the metadata orchestration hub for startup, shutdown, clean restore, fast restart, and upgrade preparation.
