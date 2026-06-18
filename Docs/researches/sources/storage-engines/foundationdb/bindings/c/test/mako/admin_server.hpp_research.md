# sources/storage-engines/foundationdb/bindings/c/test/mako/admin_server.hpp

## Purpose
Declares Mako's admin IPC protocol and `AdminServer` process wrapper.

## Important APIs, types, and functions
`DefaultResponse`, `PingRequest`, `StopRequest`, `Request`, and `AdminServer` define the serialized protocol. `sendObject`, `receiveObject`, and typed `send` move Boost-serialized objects over process pipes.

## Control flow
Construction creates pipes and starts the child. `send` serializes a request and blocks for the matching response. Copy/move are disabled.

## State and persistence behavior
State is child pid and pipe streams; no database/file persistence is declared.

## Dependencies and integration points
Depends on Boost process/serialization, `fdb_api.hpp`, `logger.hpp`, and `mako.hpp`.

## Risks and test signals
Adding request types requires updates to the variant, serialization, and dispatch. Assertions guard parent-side sends and logger process kind.
