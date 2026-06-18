# sources/sync-backup/kopia/repo/repository_test.go

Purpose: integration test suite for repository behavior across format versions and API/direct paths.

Important APIs/types/functions: tests use `formatSpecificTestSuite`, `writeObject`, `verify`, `verifyNotFound`, `mustParseObjectID`, and `ensureMapEntry`. Covered tests include writer ID stability, packing/dedup, HMAC formats, reader not-found, format-specific expected IDs, writer scope, retention blob handling, retention on object writes, write-session callbacks and failure flushing, password change, metrics, metric registry mapping, and `DeriveKey`.

Control flow: suite cases create repotesting environments for format versions, write objects through repository writers, flush/reopen repositories, compact indexes, and verify readback. Writer-scope tests create multiple independent writers and assert unflushed visibility isolation before and after flush. Retention tests wrap storage behavior through versioned maps and before-operation hooks. API callback tests connect through a test server and reuse write-session semantics.

State and persistence behavior: exercises real repository config, format blobs, blobcfg blobs, object/content blobs, content indexes, manifests, and cache/metrics state. It verifies that unflushed writer content remains private, flush makes content globally visible, retention settings protect selected blob prefixes, and changed passwords reopen only in supported formats.

Dependencies/integration: uses `repotesting`, `servertesting`, cache storage, epoch/indexblob prefixes, content/object/format internals, metrics IDs, and before-operation blob wrappers.

Risks: deterministic object ID expectations are brittle but intentional compatibility guards. Tests assume timing thresholds for metrics duration and Windows timestamp behavior in manifest replacement. Retention tests depend on storage wrapper behavior.

Test signals: very strong integration coverage for repository invariants; it does not directly exercise all open-time upgrade-lock branches but covers most direct user-visible repository operations.
