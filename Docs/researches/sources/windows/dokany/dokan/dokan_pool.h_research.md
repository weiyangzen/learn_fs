# File Research: sources/windows/dokany/dokan/dokan_pool.h

Internal header for Dokan global thread pool and reusable object-buffer pools.

Key responsibilities:
- Defines event pull timeout and main pull thread count bounds.
- Defines batch event context sizing and `DOKAN_IO_BATCH_SIZE`.
- Defines default extra event result sizes for 16K, 32K, 64K, and 128K buffers.
- Declares thread-pool lifecycle functions `GetThreadPool`, `InitializePool`, and `CleanupPool`.
- Declares pop/push/free APIs for IO batch buffers, IO event buffers, event result buffers, open-info objects, and directory-list vectors.

Important behavior:
- `BATCH_EVENT_CONTEXT_SIZE` is four times `EVENT_CONTEXT_MAX_SIZE`, allowing the driver to return multiple event contexts per pull.
- Extra result sizes are expressed as `FIELD_OFFSET(EVENT_INFORMATION, Buffer) + payload_size`, matching variable-sized reply buffers.

Dependencies:
- Includes `dokani.h`, so this internal pool API sees all core Dokan runtime types.

Notable risks:
- The header exposes pool ownership conventions only by function naming; callers must know whether a returned object came from a pool and whether direct freeing is allowed.
- Size constants must remain synchronized with driver protocol maximums and `CreateDispatchCommon()` selection logic.
