# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/message.c

Generic ISAKMP message engine.

It allocates, references, queues, frees, parses, validates, encrypts, decrypts, sends, receives, duplicates-checks, and indexes ISAKMP messages. Incoming messages are checked for header length/version/exchange/flags/message-ID validity, associated with existing or new exchanges/SAs, optionally decrypted with DOI-provided IV state, packet-logged, payload-sorted, generically validated, authenticated when HASH validation succeeds, and dispatched to exchange logic.

Payload parsing enforces generic header bounds, reserved fields, minimum sizes, next-payload validity, accepted payload sets, and nested SA/proposal/transform containment. Validation covers SA DOI/situation parsing, proposal/transform monotonic ordering, transform IDs and attributes, ID/key/nonce/cert/cert-req/vendor/NAT-D/NAT-OA/notify/delete/hash payloads, authenticated DELETE requirements, DOI/protocol checks, SPI size and length checks, and peer-address checks for DELETE authorization.

Outgoing support builds headers, appends payloads while maintaining next-payload links and payload indexes, constructs SA/proposal/transform payloads from selected protocols and DOI SPI allocation, coalesces and pads payloads before encryption, updates IVs, queues messages on normal or prioritized transport queues, sends informational NOTIFY/DELETE/DPD exchanges, and runs post-send hooks.

SA negotiation walks transform payloads bottom-up to select the first compatible protection suite, backtracking when a full-suite validator rejects a partially compatible choice. Duplicate handling retransmits the previous final response when appropriate and clears old retransmit state once the peer progresses.
