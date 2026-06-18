# File Research: sources/os/linux/linux-stable/fs/netfs/rolling_buffer.c

Implements folio_queue-based rolling buffers shared by read/write issuers and collectors.

Key behavior:
- Allocates and frees traced `folio_queue` objects.
- Initializes rolling buffers with separate head/tail pointers and an `ITER_SOURCE` or destination folio_queue iterator.
- Adds new queue nodes when the head fills while keeping iterator state valid for producer/consumer independence.
- Loads readahead folios into the buffer and records folio order.
- Appends individual folios, optionally setting mark bits.
- Deletes spent queue nodes but keeps the final placeholder queue to avoid collapsing producer/consumer pointers.
- Clears buffers and releases marked folios in batches.

Use:
- Read collection consumes folios from tail while read issue fills head.
- Write issue appends folios while write collection releases them after all streams cover them.
