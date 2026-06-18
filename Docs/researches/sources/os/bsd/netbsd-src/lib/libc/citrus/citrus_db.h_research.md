# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db.h

Public internal interface for Citrus compiled DB readers.

Key behavior:
- Forward-declares `_citrus_db`.
- Defines `_citrus_db_locator` with saved hash value and next offset.
- Declares open, close, raw lookup, string lookup, typed lookup, entry count, and indexed entry retrieval.
- Provides `_citrus_db_locator_init`.

This header is consumed by lookup, ESDB, pivot, and locale category loaders.
