# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_impl.h

This header declares internal High Sierra/ISO filesystem routines and globals.

Core routines:
- Page writeback helper `hsfs_putapage()`.
- Sector read helper `hs_readsector()`.
- Node construction/reconstruction from directory entries and disk locations.
- Directory lookup and hash lookup.
- Node free and hash synchronization.
- Directory parsing and directory entry filling.
- Name conversion for ISO/High Sierra, Joliet, and uppercase handling.
- Access checks and date parsing.
- Bogus-disk warning logging and directory validation.
- hsnode cache init/fini.

Globals:
- Vnode ops template and vnode ops pointer.
- Mount table lock and mount table list head.

Dependencies and relationships:
- Depends on structures declared in HSFS node/specification headers.
- Serves as the internal function declaration hub for HSFS implementation files.
