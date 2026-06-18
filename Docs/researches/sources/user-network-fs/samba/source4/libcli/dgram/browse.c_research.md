# sources/user-network-fs/samba/source4/libcli/dgram/browse.c

Purpose: encodes, sends, replies to, and parses NetBIOS browse mailslot datagrams.

Important APIs: `dgram_mailslot_browse_send()` serializes an `nbt_browse_packet` with NDR and sends it to `NBT_MAILSLOT_BROWSE`; `dgram_mailslot_browse_reply()` serializes a reply and sends it back to the source address/name from an incoming datagram; `dgram_mailslot_browse_parse()` extracts mailslot data and decodes it into an `nbt_browse_packet`.

Control flow: send/reply functions allocate a temporary talloc context, NDR-push browse data into a `DATA_BLOB`, construct or reuse NetBIOS names and socket addresses, call `dgram_mailslot_send()`, and free the temporary context. Parse obtains the mailslot payload via `dgram_mailslot_data()`, runs `ndr_pull_nbt_browse_packet`, logs failures, and optionally saves the bad packet at debug level 10.

State and persistence: no long-lived state is stored. A debug-only artifact `browse.dat` can be written on parse failure at high debug level, which is the only disk side effect.

Dependencies and integration: depends on `libdgram.h`, socket addressing, resolver/NBT NDR definitions, and parameter utilities. It integrates with the generic datagram mailslot sender and dispatcher.

Risks: packet size and NDR validity depend on generated NBT parsers. The reply path trusts source fields from the parsed datagram enough to build the destination. Test signals include round-trip browse packet encode/decode, malformed payload parse failure, and reply address construction from incoming packets.
