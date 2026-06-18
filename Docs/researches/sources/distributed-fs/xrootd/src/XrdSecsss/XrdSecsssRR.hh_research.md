# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssRR.hh

Purpose: defines the SSS wire-format request/response headers and encrypted data tags.

Important types: `XrdSecsssRR_Hdr` is the unencrypted protocol header with protocol ID, key-name size, encryption type, and key ID. `XrdSecsssRR_Hdr2` extends it with a padded key name for V2 clients. `XrdSecsssRR_DataHdr` carries random bytes, generation time, padding, and options. `XrdSecsssRR_Data` defines max/min payload sizes and typed fields for identity, attributes, credentials, login ID, and host. `XrdSecsssRR_DataResp` is a short server response.

Control flow: protocol code casts raw credential buffers to these structs, encrypts/decrypts the data header and payload, and iterates `<type><packed value>` entries.

State and persistence: no persistent state. Constants encode compatibility constraints for V1 and V2 peers.

Dependencies and integration: includes integer/time headers and `XrdSecsssKT.hh` for key-name size. Used by protocol, entity serialization, and ID mapping.

Risks: layout is ABI/wire-format critical; padding, endian conversion, and struct sizes must remain stable. Comments say protocol ID is `"sss"` while the field is four bytes and code copies the null terminator. Max size constants must match protocol buffer checks.

Test signals: static assertions or serialization tests for struct sizes, V1/V2 packet round trips, malformed type streams, max credential payloads, and key-name padding/termination.
