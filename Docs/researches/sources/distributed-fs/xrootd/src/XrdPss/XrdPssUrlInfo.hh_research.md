# sources/distributed-fs/xrootd/src/XrdPss/XrdPssUrlInfo.hh

## Purpose

`XrdPssUrlInfo.hh` declares the per-request URL helper used by PSS to expose path, CGI suffix construction, trace identity, and optional session/entity ID generation.

## Important APIs, Types, And Functions

- Constructor `XrdPssUrlInfo(XrdOucEnv*, const char*, const char*, bool, bool)` captures request environment data and extra CGI policy.
- `addCGI()`, `Extend()`, `hasCGI()`, `thePath()`, `Tident()`, and `getID()` are the primary URL-building accessors.
- `setID(const char*)` derives an ID from trace or entity state.
- `setID(XrdOucSid*)` obtains a session ID and formats `p<sid>@`.
- Static `setMapID(bool)` selects security-entity ID mapping behavior.

## Control Flow

The header exposes a two-step use pattern: construct from request environment, optionally extend CGI and set an ID, then ask `addCGI()` for a protocol-appropriate suffix. Destructor cleanup only matters for session IDs acquired from `XrdOucSid`.

## State And Persistence

State is request-local and stored in fixed buffers plus borrowed pointers. `MapID` is process-global. `idVal` tracks a borrowed session ID lease when used.

## Dependencies And Integration Points

The header forward-declares `XrdOucEnv` but directly uses `XrdOucSid` types without including its header, relying on include order from users. It integrates with PSS URL generation and persona mapping.

## Risks And Edge Cases

- Missing direct declarations for `XrdOucSid` make the header fragile unless included after a header defining it.
- Fixed-size `theID[13]` and `CgiSfx[512]` impose silent formatting limits enforced in the implementation.
- Destructor behavior depends on `theID` beginning with `p` to release a session ID.

## Test Signals

Compile tests should include this header in isolation or document required include order. Runtime tests should validate ID lifetime and suffix construction through the public API.
