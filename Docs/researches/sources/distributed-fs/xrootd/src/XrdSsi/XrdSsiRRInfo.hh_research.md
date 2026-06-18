# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiRRInfo.hh

Purpose: defines compact request/response protocol metadata encoded into XRootD file offsets and attention responses. It is the wire-format helper used by `XrdSsiFileSess` and clients.

Important APIs/types: `XrdSsiRRInfo` stores an operation command in the top byte of `reqId`, a 24-bit request ID, and a 32-bit request size. `Opc` values are `Rxq`, `Rwt`, and `Can`. Methods set/get command, ID, size, raw data pointer, and packed `Info()`. `XrdSsiRRInfoAttn` describes attention responses with tag values `alrtResp`, `fullResp`, and `pendResp`, plus prefix and metadata lengths.

Control flow and state: setters use network byte order for ID/size, preserving the command byte during ID changes. `Info()` packs the stored network-order fields into a 64-bit value for file offsets. There is no dynamic allocation or persistence.

Dependencies and integration: depends on `arpa/inet.h` and response info definitions. Used by file-session `write()`, `read()`, `truncate()`, and `fctl()` to identify requests and commands. Risks include 24-bit ID wrap/collision, endian correctness, union aliasing assumptions, and callers confusing request size with actual write length. Test signals should cover pack/unpack across commands, max ID masking, zero-size requests, cancellation offsets, and attention-header network byte order.
