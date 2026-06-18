# File Research: sources/local-fs/xfsdump/inventory/inventory.h

Public inventory API header for xfsdump/xfsrestore clients.

Key contents:
- Defines inventory path macros, filename suffixes, inventory versions, packed inventory versions, and print-depth constants.
- Defines open predicates (`INV_BY_UUID`, `INV_BY_MOUNTPT`, `INV_BY_DEVPATH`) and open modes (`INV_SEARCH_ONLY`, `INV_SEARCH_N_MOD`).
- Defines public exported session model: `inv_mediafile_t`, `inv_stream_t`, and `inv_session_t`.
- Opaquely declares token pointer types for inventory, session, and stream access.
- Declares lifecycle APIs: `inv_open()`, `inv_close()`, write-session open/close, stream open/close, mediafile append.
- Declares query APIs for last lower/equal dump level, session lookup by UUID/label, and session freeing.
- Declares packed session APIs for dump/restore reconstruction and inventory debug/printing helpers.
- Declares inventory path setup/accessors.

Important design:
- Public callers never see on-disk private structs directly.
- Write path is hierarchical: inventory token -> session token -> stream token -> mediafiles.
- Reconstruction path bypasses token lifecycle using packed session info.

Notable observations:
- Header documents that inventory is intentionally dump/restore-specific, not a generic database.
