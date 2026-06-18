# sources/distributed-fs/xrootd/src/XrdSecztn/XrdSecztn.cc

## Purpose
Provides a local helper for deciding whether a bearer token string looks like a JWT. It decodes the base64url header segment and checks for a JSON header containing `"typ":"JWT"`.

## Important APIs, Types, And Functions
- `XrdSecztn::isJWT(const char *b64data)` is the exported helper used by `XrdSecProtocolztn.cc`.
- Anonymous namespace `DecodeBytesNeeded()` sizes a decode buffer.
- Anonymous namespace `DecodeUrl()` performs a base64url-compatible decode using `b64Table`.
- `b64Table` maps ASCII byte values to base64 values or invalid markers.

## Control Flow
`isJWT()` strips a leading `Bearer%20` prefix, finds the first dot, copies only the header segment into a stack buffer, allocates stack decode space, and decodes the segment. The decoded header must start with `{`, end with `}`, contain `"typ"`, then a colon and optional spaces, then `"JWT"`. A failure at any point returns false.

## State And Persistence
The file has only constant lookup-table state. It allocates temporary stack memory with `alloca()` and has no persistent state.

## Dependencies And Integration Points
Uses C/C++ runtime headers and platform-specific `alloca.h`. The only visible integration is the `XrdSecztn` namespace symbol consumed by the ztn security protocol implementation.

## Risks And Edge Cases
- `b64Table[ch]` indexes with `uint8_t`, so high-byte input stays in range, but the table is shorter than 256 entries by inspection risk should be verified at compile time.
- The JSON test is deliberately shallow and whitespace-limited. It does not parse JSON and may reject valid JWT headers with formatting differences or lowercase/alternate typ conventions.
- It accepts `Bearer%20` but not plain `Bearer `.
- It only inspects the header, not signature or claims, which is appropriate for filtering but not validation.

## Test Signals
Exercise JWTs with and without `Bearer%20`, invalid base64url characters, missing dot, long header segment, decoded non-JSON, typ value absent, spaces around the colon, and valid headers with additional fields.
