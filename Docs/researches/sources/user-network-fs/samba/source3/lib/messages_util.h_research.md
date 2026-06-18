# sources/user-network-fs/samba/source3/lib/messages_util.h

## sources/user-network-fs/samba/source3/lib/messages_util.h

Purpose: Publishes the internal messaging header layout contract for source3 messaging utilities.

Important APIs/types/functions: Defines `MESSAGE_HDR_LENGTH` as `52` and declares `message_hdr_put()` and `message_hdr_get()` over a fixed-size `uint8_t buf[MESSAGE_HDR_LENGTH]`. It forward-declares `struct message_hdr`, although the exposed helpers operate on raw bytes and `struct server_id`.

Control flow: Consumers include this header to build or parse message headers before sending through messaging transport code.

State and persistence behavior: The constant is persistent protocol state for in-memory and IPC message frames. No storage is owned here.

Dependencies and integration points: Coupled to `lib/util/server_id.h` users and `messages_util.c`; included by messaging implementations and tests that need deterministic header construction.

Risks: Changing the constant or prototype breaks ABI/source consumers and serialized headers.

Test signals: Compile coverage plus `message_hdr_put/get` round-trip tests are the main signal.
