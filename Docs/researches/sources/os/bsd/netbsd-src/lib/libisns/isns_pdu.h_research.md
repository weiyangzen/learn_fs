# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_pdu.h

Declares libisns PDU, transaction, TLV, and buffer-pool data structures. It defines the iSNS protocol version, max PDU payload size, default pool sizes, buffer ownership types, and transaction completion flags.

Key contents:
- `struct isns_buffer_s`: length/type/next metadata preceding buffer data.
- `ISNS_INIT_BUFFER()` and `isns_buffer_data()` macros for embedded buffer layout.
- TLV helpers using `memcpy()` plus `isns_htonl/isns_ntohl`, avoiding unaligned access for TLV headers.
- `struct isns_trans_s`: transaction id/function/flags, config pointer, TLV iterator state, request/response PDU lists, disconnect count.
- `struct isns_pdu_s`: config pointer, wire header, host-byteorder marker, payload buffer list, next PDU link.
- Macros for accessing request/response heads and transaction flags.

This header is the central private contract between the iSNS PDU, task, thread, and utility modules.
