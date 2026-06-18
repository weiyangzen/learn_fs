# File Research: sources/virtualization/nbdkit/plugins/vddk/vddk-stubs.h

Macro include file listing VDDK API functions that the plugin resolves with `dlsym`.

Key behavior:
- Must be included with `STUB(fn, ret, args)` and optionally `OPTIONAL_STUB(fn, ret, args)` defined by the including file.
- Required APIs include initialization/exit, transport listing, error text handling, connection parameter allocation/free, connect/open/close/disconnect, info/free-info, read/write, create, flush, async read/write, wait, allocated-block queries, free-block-list, and allocate-connect-params.
- Comments document version provenance:
  - Baseline required stubs from VDDK 6.5-era support.
  - Flush/read-async/write-async added in VDDK 6.0.
  - Wait added in VDDK 6.5.
  - QueryAllocatedBlocks/FreeBlockList/AllocateConnectParams added in VDDK 6.7.
- `OPTIONAL_STUB` is retained for future compatibility but currently unused because VDDK >= 6.7 is required.

Role:
- Provides one source of truth for function pointer declarations, symbol loading, stats objects, dump-plugin symbol reporting, and statistics collection.
