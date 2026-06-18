# sources/sync-backup/casync/src/caprotocol.h

## Purpose
`caprotocol.h` defines the binary frame protocol spoken between `CaRemote` and helper subprocesses such as `casync-http` or remote `casync` over ssh. It describes pull and push handshakes, frame type IDs, feature flags, and packed frame structures.

## Important APIs, Types, and Functions
The enum of frame type constants assigns fixed 64-bit magic values to hello, file streaming, request, chunk, missing, goodbye, and abort frames. `CaProtocolHeader` carries little-endian size and type fields; `CA_PROTOCOL_SIZE_MIN` and `CA_PROTOCOL_SIZE_MAX` bound frame size. Structures include `CaProtocolHello`, `CaProtocolFile`, `CaProtocolFileEOF`, `CaProtocolRequest`, `CaProtocolChunk`, `CaProtocolMissing`, `CaProtocolGoodbye`, and `CaProtocolAbort`. Feature flags distinguish services provided, such as readable/writable store/index/archive, from requested operations, such as pulling or pushing chunks/index/archive.

## Control Flow
The comment block documents the protocol: both sides send hello; pull sends index from server then client requests chunks and receives chunks; push sends index from client then server requests chunks and receives chunks or missing markers; goodbye and abort terminate flows.

## State and Persistence
This header defines wire state, not runtime state. Frames are serialized with little-endian integer fields and flexible payload arrays. The maximum frame size is 16 MiB.

## Dependencies and Integration Points
It includes `util.h` for endian types and `cachunkid.h` for chunk ID size. `caremote.c` validates and emits these frames, while `casync-http.c` feeds HTTP/FTP/SFTP data into the same frame stream.

## Risks
The protocol uses C structs with flexible arrays as wire overlays; all readers must validate sizes before access. Any change to constants or layout breaks compatibility. The comment says `CA_PROTOCOL_ABORTED` in one sentence, while the actual constant is `CA_PROTOCOL_ABORT`.

## Test Signals
Remote/protocol behavior is exercised indirectly by integration tests that set `CASYNC_PROTOCOL_PATH` and run casync script flows. Frame-level fuzz tests exist under `test/fuzz` generally, but no specific direct test was visible in this read.
