# File Research: sources/os/bsd/netbsd-src/lib/libresolv/ns_sign.c

Read completely: 393 lines.

Constructs TSIG records and appends them to DNS messages. `ns_sign()` delegates to `ns_sign2()`, which writes the TSIG owner name, type/class/TTL/RDLEN, algorithm, time signed, fudge, signature, original message id, error, and optional BADTIME other-data fields.

For normal signing, it only accepts `KEY_HMAC_MD5`. The digest covers any query signature for responses, the original message, canonical key name, class/TTL, canonical algorithm name, time/fudge, error, and other-data. Generated signatures are returned to the caller and copied into the TSIG RDATA.

The TCP helpers maintain `ns_tcp_tsig_state`, chaining the previous signature into the next MAC and emitting TSIG records on the first message, every 100 messages, or the final message. Buffer boundary checks return `NS_TSIG_ERROR_NO_SPACE`.
