# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonData.hh

Purpose: defines the wire-format data structures, stream codes, operation codes, masks, and file-stat record layouts used by XRootD monitoring packets.

Important APIs/types/functions: packet structs include `XrdXrootdMonHeader`, `XrdXrootdMonTrace`, `XrdXrootdMonBuff`, `XrdXrootdMonRedir`, `XrdXrootdMonBurr`, `XrdXrootdMonGS`, and `XrdXrootdMonMap`. File-stat structs include `XrdXrootdMonFileHdr`, `XrdXrootdMonFileTOD`, `XrdXrootdMonFileLFN`, `XrdXrootdMonFileOPN`, `XrdXrootdMonStatPRW`, `XrdXrootdMonStatOPS`, `XrdXrootdMonStatSSQ`, `XrdXrootdMonStatXFR`, `XrdXrootdMonFileCLS`, `XrdXrootdMonFileDSC`, and `XrdXrootdMonFileXFR`.

Control flow: this header has no executable flow; producers fill these structures in network byte order and consumers decode based on stream `code`, record `recType`, flags, and variable `recSize`.

State and persistence behavior: no local state. The structures define persisted UDP payloads as observed by collectors and downstream monitoring systems.

Dependencies: `XProtocol/XPtypes.hh` for fixed protocol integer aliases. Producers rely on byte-order helpers from platform headers.

Integration points: used by `XrdXrootdMonitor`, `XrdXrootdMonFile`, `XrdXrootdGSReal`, redirect monitoring, dictionary mapping, and external collectors.

Risks: ABI/wire compatibility is fragile: field sizes, signedness, and endianness must stay stable. Several structures are variable-length despite C declarations with placeholder arrays, so producers must use `recSize` and computed lengths rather than `sizeof` blindly. Comments mention spelling/semantic quirks such as `hasSSQ`/`hasCSE` sharing a value.

Test signals: binary packet decoding against known fixtures; endianness on big- and little-endian hosts; variable close/open records with and without LFN/OPS/SSQ; redirect records with host/path truncation; G-Stream SID encoding; collector compatibility across versions.
