# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/compress.c

Van Jacobson TCP/IP header compression for PPP. It keeps transmit and receive header state tables, compresses eligible non-fragmented TCP ACK/data packets by encoding changed sequence, ack, window, urgent, and IP id fields, and emits compressed, uncompressed-VJ, or plain IP protocol ids.

Decompression restores headers from saved state, handles explicit/implicit connection ids, reconstructs TCP/IP length and checksum fields, and discards packets after line errors until state is resynchronized. Negotiation records whether connection ids are compressed.
