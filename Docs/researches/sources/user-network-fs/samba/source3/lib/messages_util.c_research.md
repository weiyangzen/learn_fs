# sources/user-network-fs/samba/source3/lib/messages_util.c

## sources/user-network-fs/samba/source3/lib/messages_util.c

Purpose: Serializes and deserializes Samba internal messaging headers into a fixed 52-byte wire/storage buffer.

Important APIs/types/functions: `message_hdr_put()` writes destination `server_id`, source `server_id`, and `msg_type`. `message_hdr_get()` reads those fields back. The code relies on `SERVER_ID_BUF_LENGTH`, `server_id_put()`, `server_id_get()`, `SIVAL()`, and `IVAL()`.

Control flow: Put writes destination at offset zero, source at `SERVER_ID_BUF_LENGTH`, and the 32-bit type after two server-id slots. Get performs the inverse and intentionally returns source and destination through distinct pointers.

State and persistence behavior: No durable state beyond the caller-provided byte array. The exact byte order and fixed length are the compatibility contract.

Dependencies and integration points: Used by source3 messaging paths that prepend message metadata before payload bytes. Depends on Samba byteorder and NDR/server-id utilities.

Risks: Header length must match serialized `server_id` size. Field order is easy to reverse, so tests should round-trip asymmetric source/destination ids.

Test signals: Unit tests should validate buffer length, message type endian behavior, and round trips for unique, broadcast, and disconnected server ids.
