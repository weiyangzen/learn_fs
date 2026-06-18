# File Research: sources/virtualization/spdk/lib/blob/request.h

Private request API for blobstore asynchronous work. It defines completion variants for blobstore operations, blob operations, blob-id returns, blob-handle returns, and nested sequences.

`struct spdk_bs_request_set` is the central reusable state object. It contains the user completion, accumulated error, owning blobstore channel, optional backing device channel for external snapshot clones, low-level `spdk_bs_dev_cb_args`, a union for sequence/batch/user-op state, optional extended I/O options, and a queue link.

The header declares:
- sequence lifecycle and device I/O helpers,
- batch open/read/write/unmap/write-zero/close helpers,
- sequence-to-batch conversion,
- deferred user-op allocation/execution/abort helpers,
- the shared completion dispatcher `bs_call_cpl()`.

It is the internal contract between blob metadata/data paths and the channel request-pool implementation.
