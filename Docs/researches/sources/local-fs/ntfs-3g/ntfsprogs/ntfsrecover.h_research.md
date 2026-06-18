# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsrecover.h

This header defines the shared declarations for NTFS log recovery processing. It provides unaligned little-endian accessor macros, the NTFS log action enum used by `ntfsrecover.c`, and the core variable-length structures used for block caching, queued actions, and tracked attribute metadata.

`enum ACTIONS` assigns stable numeric IDs for known NTFS log operations from `Noop` through Windows 10-specific actions, with `LastAction` expected to equal 38. `struct BUFFER` wraps a cached restart or record block with logical/read block numbers, size, computed header size, and USA-safety status. `struct ACTION_RECORD` links copied `LOG_RECORD` instances for backward replay. `struct ATTR` tracks logged attribute table entries by key, inode, LSN, type, and optional UTF-16 name.

The header exports the global geometry, log, option, counter, restart, and client variables owned by the recovery implementation. It also declares helper functions for action names, MFT attribute names, UTF-16 name display, attribute-table management, redo/undo/extra offset calculation, LCN filtering, exception checking, and hex dumping.

Replay integration is intentionally externalized through `play_undos`, `play_redos`, `show_redos`, and `freeclusterentry`, allowing the parser/display file to call into the mutation engine implemented elsewhere. Correctness depends on the struct layout matching checks in `ntfsrecover.c` and on callers preserving the variable-length “keep at the end” layout of `BUFFER`, `ACTION_RECORD`, and `ATTR`.
