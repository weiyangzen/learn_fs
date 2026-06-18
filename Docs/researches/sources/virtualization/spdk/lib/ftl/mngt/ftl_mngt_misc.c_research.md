# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_misc.c

Miscellaneous management steps for configuration, memory pools, relocation/NV-cache init, scrubbing, startup finalization, poller control, maps, trim metadata, and property APIs.

Important content:
- Config validation delegates to `ftl_conf_is_valid`.
- P2L map pool is backed by SHM metadata and initialized differently for fast versus non-fast startup.
- Band metadata pool is a normal mempool.
- Relocation and NV-cache init/deinit wrap `ftl_reloc_init/free` and `ftl_nv_cache_init/deinit`.
- NV-cache scrub runs on first create or major upgrade, clearing active cache chunks to avoid stale recovery data.
- Startup finalization detects in-progress trims, registers superblock version property, clears limit stats, marks initialization/SHM-ready, and resumes L2P, relocation, writers, and NV cache.
- Core poller start/stop controls main FTL progress loop; stop waits while poller exists.
- Valid and trim maps are bitmap wrappers over metadata buffers.
- Trim metadata/log clearing use async metadata clear callbacks.
- Property get/set APIs marshal work to the core thread and run property decode/set through management processes with cleanup.

This file binds operational controls around the core FTL data path.
