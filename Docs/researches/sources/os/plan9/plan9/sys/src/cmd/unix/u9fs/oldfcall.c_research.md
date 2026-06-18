# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/oldfcall.c

- Role: Bridges old 9P1 wire messages to the newer `Fcall` structure used by the server.
- Key functions: `oldhdrsize`, `iosize`, `convM2Sold`, `convS2Mold`, `convM2Dold`, `convD2Mold`, `sizeS2M`, and `sizeD2Mold`.
- Control flow: Incoming old opcodes are decoded into modern `Twalk`, `Topen`, `Tread`, etc.; outgoing responses are re-encoded as fixed-format 9P1 messages.
- Compatibility details: Maps old clone/walk semantics into `Twalk`; squashes Qid path/type through `FIXQID`; treats old session as a special flush/session response path.
- Risks/notes: Fixed 28/64/116 byte fields mirror legacy protocol limits; string fields point into the receive buffer rather than owned memory.
