# sources/sync-backup/casync/src/cafileroot.h

## Purpose
Defines `CaFileRoot`, a small reference-counted root descriptor used by locations to reopen files relative to a stable root path or fd.

## Important APIs, Types, and Functions
`struct CaFileRoot` contains `n_ref`, `path`, `fd`, and `invalidated`. Public functions are `ca_file_root_new`, `ca_file_root_ref`, `ca_file_root_unref`, and `ca_file_root_invalidate`.

## Control Flow
No runtime logic lives in the header. It declares the lifecycle that `calocation.c` uses for root ownership.

## State and Persistence Behavior
The fields represent in-memory attachment state. `invalidated` is the signal that cached file origins should no longer be opened.

## Dependencies and Integration Points
Requires `<stdbool.h>`. It is included by `calocation.h`, making root attachment part of the public location API.

## Risks
The struct is public rather than opaque, so callers can mutate fields directly and bypass reference/invalidation rules. Reference counts are plain integers.

## Test Signals
ABI compile checks and location-open tests with valid and invalidated roots cover the header contract.
