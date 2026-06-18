# sources/object-store/minio/cmd/metacache_test.go

Purpose: This test file validates small but important metacache lifecycle helpers: base-directory derivation, finished-state detection, and cache-retention decisions.

Important APIs and types: It defines `metaCacheTestsetTimestamp` and `metaCacheTestset`, a slice of representative `metacache` values covering normal success, recursive success, older success, error, stale started, not-found success, older recursive success, running, and week-old finished cases. Tests call `baseDirFromPrefix`, `metacache.finished`, and `metacache.worthKeeping`.

Control flow: `Test_baseDirFromPrefix` checks root object, dot-slash, slash, folder, folder/object, nested folder/object, and nested folder prefixes. `Test_metacache_finished` compares each fixture against expected end-time-derived booleans. `Test_metacache_worthKeeping` checks which caches should survive according to age, status, and last-handout/update rules.

State and persistence behavior: No persistent state is created. The fixtures model persisted metacache records by setting timestamps and status fields directly. Retention expectations are time-relative to `time.Now()` at package initialization, so the tests simulate stale records by subtracting minutes or days.

Dependencies and integration points: These tests protect logic used by the metacache manager cleanup path and listing request routing. `baseDirFromPrefix` also affects cache sharing and scan roots derived from list prefixes.

Risks: The `worthKeeping` test contains a TODO and uses real current time rather than an injected clock, so it is sensitive to long pauses between fixture initialization and assertions. It does not cover `keepAlive`, `update`, or `delete`, which have more complex interactions with peers and object-layer state.

Test signals: Exact expected base directory strings, `finished` true only when `ended` is non-zero, and retention booleans for stale running, old failed, recent success, and week-old finished caches.
