# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwBadCS.cc

Purpose: implements per-request bad-checksum collection for pgwrite and formats correction information returned to clients.

Important APIs/types/functions: `boAdd()` records one bad data extent and `boInfo()` returns an optional `ServerResponseBody_pgWrCSE` plus bad-offset vector.

Control flow: `boAdd()` traces the checksum error, initializes or updates first/last bad-data lengths, rejects the request if the per-request maximum would be exceeded, stores the bad file offset in network order, and inserts the extent into the file-level `pgwFob` uncorrected-offset set. `boInfo()` returns no payload when no bad offsets were recorded; otherwise it computes the correction-extension CRC and returns a pointer to the packed response body.

State and persistence behavior: per-request `boCount`, `badOffs[]`, and `cse` response struct are in memory. File-level uncorrected checksum state persists for the life of `XrdXrootdPgwFob` and is logged at file close/destruction.

Dependencies: `XrdOucCRC`, `XrdSysPlatform`, `XrdXrootdFile`, `XrdXrootdPgwFob`, protocol page-write response structs, and tracing.

Integration points: called from `XrdXrootdPgrwAio::VerCks()` and from `SendDone()` to include correction data in pgwrite final responses.

Risks: limit check uses `boCount+1 >= kXR_pgMaxEpr`, which permits one fewer stored offset than a strict `< max` interpretation. `boInfo()` returns a pointer to internal mutable storage, so callers must send before reset/destruction. File-level `addOffs()` failure turns into a request error even if the current page write otherwise proceeds.

Test signals: zero-error response, one and many bad offsets, first/last data-length encoding for unaligned pages, correction CRC validation, per-request limit, per-file uncorrected-offset limit, and trace output.
