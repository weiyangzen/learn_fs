# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucReqID.cc

Purpose: implements request identifier generation and ownership decoding. IDs combine a local or encoded network prefix, CRC hash, timestamp, and monotonically increasing sequence number so request flows can identify origin and distribute keys across slots.

Important APIs, types, and functions: constructors build the ID format string and prefix; `ID()` emits the next ID under `myMutex`; `isMine()` compares an incoming ID with `reqPFX` and can decode alternate host/port information; `Index()` maps arbitrary key bytes to a modulo bucket using `XrdOucCRC::CRC32`.

Control flow: the default constructor formats the process ID and epoch time into a short local prefix and printf template. The address-aware constructor uses `XrdNetUtils::Encode()` to encode a socket address and port, falls back to port/time formatting if encoding fails, hashes the prefix, and builds a longer template. `ID()` increments `reqNum`, writes the formatted ID, and returns either the full buffer or the post-prefix internal part depending on `reqIntern`. `isMine()` first checks the prefix, otherwise tries to decode a host from the request ID.

State and persistence: persistent process-local state includes duplicated strings for the prefix and format, sequence number, and mutex. IDs are not persisted across process restarts; uniqueness relies on process/time/address prefix plus sequence. The destructor intentionally leaves static-style allocations to process exit.

Dependencies and integration points: depends on `XrdSysMutex`, `XrdNetAddr`, `XrdNetUtils`, `XrdOucCRC`, libc time/PID/string calls, and socket address types. It integrates with routing, request tracking, and any code needing stable modulo assignment through `Index()`.

Risks and test signals: callers must provide `ID()` buffers large enough for the formatted string despite only a comment documenting `blen >= 48`. `snprintf(buff, blen-1, ...)` leaves one byte unused and depends on positive lengths. `reqNum` can eventually wrap. Tests should verify format stability, concurrent `ID()` uniqueness, `isMine()` for local and remote IDs, fallback constructor behavior, and `Index()` consistency.
