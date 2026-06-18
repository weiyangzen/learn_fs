# File Research: sources/virtualization/spdk/lib/blob/request.c

Implements blobstore request-set execution. A single `spdk_bs_request_set` object is reused as a serial sequence, parallel batch, or deferred user operation, then returned to the channel free list after completion.

Major paths:
- `bs_call_cpl()` dispatches typed blobstore/blob completions, converting errors to `NULL` handles or invalid blob ids as appropriate.
- Sequence helpers allocate a request set from the channel, install callback trampoline state, optionally switch to an external snapshot backing channel, and issue reads, writes, vectored I/O, zero writes, or copy operations to either the main device or a supplied `spdk_bs_dev`.
- Batch helpers submit multiple device operations with a shared completion counter. Completion is deferred until outstanding operations reach zero and the batch has been closed.
- `bs_sequence_to_batch()` converts an active sequence into a batch for sub-operations that complete back into a sequence continuation.
- User-op helpers allocate deferred blob read/write/unmap/write-zero/readv/writev operations and later execute or abort them, returning the request set to the channel.

The code threads `ext_io_opts` into extended readv/writev paths when present, records blob request trace events, stores the first nonzero error in `set->bserrno`, and uses the same callback trampoline for both sequence and batch completion.
