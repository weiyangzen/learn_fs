# sources/sync-backup/git-lfs/lfshttp/lfshttp.go

Purpose: Defines HTTP context abstraction and JSON response decoding rules for LFS HTTP APIs.

Important APIs/types/functions: `Context`, `NewContext`, `testContext`, `IsDecodeTypeError`, `decodeTypeError`, and `DecodeJSON`.

Control flow: `NewContext` supplies default Git config and map-backed envs. `DecodeJSON` accepts only Git LFS JSON or generic JSON media types, decodes response body into the target object, closes the body, and wraps parse errors.

State and persistence behavior: Context holds config and env maps in memory. Decode consumes response bodies.

Dependencies and integration points: Used throughout `lfshttp` and `lfsapi` tests, lock API decoding, and error handling. Depends on `git.Configuration`, `config.Environment`, and shared errors.

Risks and edge cases: Empty or unexpected content type returns a typed decode error without consuming body. JSON parse errors include request method and URL context.

Test signals: Covered indirectly by response and locking tests. No standalone tests for media type regex edge cases in this subset.
