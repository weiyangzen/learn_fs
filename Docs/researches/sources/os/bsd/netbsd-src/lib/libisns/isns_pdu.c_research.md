# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_pdu.c

Implements libisns buffer pooling, transaction lifecycle, PDU construction/destruction, TLV append/read helpers, and PDU send task creation. It owns the global `G_buffer_pool`, sorted buffer-size lists, pooled versus malloc/static buffer typing, and deferred transaction freeing via `ISNS_TRANSF_FREE_WHEN_COMPLETE`.

Key behavior:
- `isns_new_trans()` allocates a transaction from an ISNS buffer, assigns a monotonically increasing transaction id, filters PDU flags, creates the first request PDU, and links it into the request list.
- `isns_send_trans()` marks first/last PDU flags, assigns sequence ids, queues a send task through `isns_send_pdu()`, and optionally reads the response status.
- `isns_add_tlv()` writes a network-order TLV header and padded payload into one or more PDU payload buffers, splitting into chained PDUs at `ISNS_MAX_PDU_PAYLOAD`.
- `isns_get_tlv()` walks completed response PDUs and buffers, materializing spanning TLV values into extra transaction-owned buffers.
- `isns_abort_trans()` completes a matching current or queued send task.

Important dependencies:
- `isns_config_s` for mutexes, server/client mode, task queue, socket state.
- `isns_task.c` for queued send task creation/wait/abort.
- `isns_util.h` byte-order and allocation macros.

Notable risks:
- `isns_get_next_trans_id()` uses a static unsynchronized `int`, so concurrent callers can race.
- Several reads cast raw buffer data to `uint32_t *`, relying on alignment that the buffer allocator mostly preserves.
- `isns_get_pdu_response_status()` uses `htonl()` when reading a network-ordered status; semantically this should be host conversion, though it is equivalent on common byte-swap implementations.
