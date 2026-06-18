# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/9p1lib.c

Serialization and deserialization helpers for 9P1 messages, dentries, tickets, and authenticators.

`convS2M9p1` and `convM2S9p1` pack/unpack all 9P1 request and response types using little-endian fixed fields. `convD2M9p1` converts cwfs `Dentry` into old fixed-length directory records, including compatibility qid rewriting for top dump filesystem levels. `convM2D9p1` decodes old stat records back into `Dentry` fields.

Authenticator and ticket converters optionally encrypt/decrypt using the supplied DES key. The file is the protocol-format boundary between legacy clients and cwfs internals.
