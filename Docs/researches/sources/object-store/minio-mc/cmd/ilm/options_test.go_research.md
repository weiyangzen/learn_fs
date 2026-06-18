# Research: sources/object-store/minio-mc/cmd/ilm/options_test.go

Purpose: unit tests for lifecycle filter construction from `LifecycleOptions`.

Important APIs/types/functions: `TestOptionFilter` and local `filterEq` comparator.

Control flow: builds expected filters for empty, prefix, tag, size-lt, size-gt, and combined predicate cases. Each test calls `opts.Filter()` and compares scalar fields and `And.Tags`.

State and persistence: no persistence; pure unit tests.

Dependencies/integration points: `testing`, `humanize`, and MinIO lifecycle types.

Risks: tests cover filter construction only, not validation or full lifecycle rule generation. Comparator is local and must evolve if lifecycle filter fields expand.

Test signals: positive test signal for the single-predicate versus `And` behavior in `Filter`.
