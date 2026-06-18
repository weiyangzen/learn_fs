# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_steps.h

Central declaration header for FTL management-step actions. It exposes startup, shutdown, metadata, layout, L2P, NV cache, trim, P2L checkpoint, self-test, superblock, and rollback functions used by management process descriptors.

Role:
- Provides the common function vocabulary for `ftl_mngt_startup.c`, `ftl_mngt_shutdown.c`, `ftl_mngt_recovery.c`, and related step implementations.
- Keeps management pipelines loosely coupled to implementation files.

Risk:
- Large flat header creates broad compile-time coupling, but it matches the management-process descriptor pattern used in this subsystem.
