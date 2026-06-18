<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/sidecar_test.py -->
# Research: sources/storage-engines/foundationdb/packaging/docker/sidecar_test.py

## Purpose
Unit/integration-style tests for the Docker sidecar HTTP handler and direct filesystem helper functions.

## Important APIs, Types, And Functions
`TestSidecar` starts a local `HTTPServer` with a `MagicMock` config. Tests exercise `SidecarHandler`, `check_hash`, and `is_present` using temporary output directories and `requests`.

## Control Flow
`setUp` allocates a free localhost port, configures no-TLS behavior, starts the server in a daemon thread, and each test makes real HTTP calls or direct helper calls. `tearDown` removes the temporary output directory.

## State And Persistence Behavior
Creates transient files under `tempfile.mkdtemp()` to verify hashes and nested file detection. No persistent repo state is changed.

## Dependencies And Integration Points
Depends on Python `unittest`, `requests`, `unittest.mock`, and the sibling `sidecar` module. This is the nearest automated signal for the sidecar HTTP contract used by Docker/Kubernetes startup probes and control calls.

## Risks And Edge Cases
The test server is not explicitly shut down, relying on daemon threads. TLS, certificate authorization, IPv6 binding, substitution rendering to monitor conf, and copy-binary/library behavior are not covered.

## Test Signals
Positive tests assert `/ready`, `/substitutions`, `/check_hash`, `/is_present`, and `POST /copy_files`; negative tests assert 404s and outside-path `RequestException`s.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/sidecar_test.py -->
