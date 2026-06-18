# sources/object-store/rustfs/crates/ecstore/src/client/api_get_object.rs

## Purpose
Contains the transition-client object GET path and a placeholder `Object` reader abstraction. The implemented async path fetches an object and buffers its body into a `ReadCloser`; the public `get_object` and `Object` read machinery are currently unsupported placeholders.

## Important APIs, Types, and Functions
- `TransitionClient::get_object` returns `Unsupported`.
- `TransitionClient::get_object_inner` sends `GET`, builds `ObjectInfo` from response headers with `to_object_info`, buffers all body frames into memory, and returns `(ObjectInfo, HeaderMap, BufReader<Cursor<Vec<u8>>>)`.
- `GetRequest`, `GetResponse`, and `Object` model a stateful reader with offset/seek/read/stat fields.
- `Object::{do_get_request, read, read_at, seek, stat, close}` mirror a lazy ranged-reader design, but `do_get_request` returns `Unsupported`.

## Control Flow and State Behavior
`get_object_inner` builds `RequestMetadata` from bucket, object, option query values, and option headers, then delegates to `execute_method`. It does not inspect HTTP status before parsing headers/body, relying on `execute_method` or `to_object_info` to fail. `Object` methods mutate offsets and state flags conceptually, but no real request path exists.

## Dependencies and Integration Points
Uses `GetObjectOptions`, `TransitionClient`, `RequestMetadata`, `ReaderImpl`, `ObjectInfo`, `ReadCloser`, `to_object_info`, `http_body_util`, `hyper::Bytes`, `EMPTY_STRING_SHA256_HASH`, and tokio readers. `fget_object` depends on `get_object`, so it inherits the unsupported behavior.

## Persistence
No local persistence. It reads object bytes from the remote endpoint and materializes them in memory.

## Risks and Edge Cases
The main public `get_object` API is not implemented. The implemented `get_object_inner` buffers whole objects, which is risky for large objects and defeats streaming. It does not enforce imported response-size limits. Lack of explicit status handling may mis-handle error bodies depending on `execute_method` behavior. `Object` methods ignore some internal errors (`oerr` is unused) and are dead/private placeholders.

## Test Signals
No inline tests. Needed tests include non-OK status behavior, range option propagation, large object streaming or limits, header-to-object-info mapping, and public `get_object` implementation once completed.
