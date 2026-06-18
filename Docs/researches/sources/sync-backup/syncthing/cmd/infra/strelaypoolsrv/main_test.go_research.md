# sources/sync-backup/syncthing/cmd/infra/strelaypoolsrv/main_test.go

Purpose: regression and utility tests for the relay pool server HTTP endpoint and URL handling.

Important APIs/tests: package-level `init` seeds `permanentRelays` and `knownRelays`; `TestHandleGetRequest` exercises `handleEndpointFull`; `TestCanonicalizeQueryValues` documents the `url.Parse` plus `Query().Encode()` canonicalization behavior; `TestSlimURL` verifies that relay URLs exposed by the short endpoint preserve only the `id` query parameter.

Control flow and state: the tests mutate package globals, so they assume single-package test execution and capacity-sensitive permanent relay setup. `TestHandleGetRequest` decodes the JSON response and then checks the global permanent relay slice for unchanged order and values.

Dependencies/integration: uses `httptest`, `encoding/json`, `net/url`, and the server package globals. It does not spin up listeners or exercise the relay testing queue.

Risks and test signals: the main regression signal is that full endpoint assembly must not corrupt `permanentRelays`. The URL canonicalization test is explanatory rather than directly invoking `handleRegister`. Gaps remain around `handleEndpointShort`, request queue backpressure, TLS certificate ID validation, IP header behavior, and error tracker blocking.
