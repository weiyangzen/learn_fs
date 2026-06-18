# sources/sync-backup/syncthing/cmd/strelaysrv/pool.go

Purpose: periodically registers a running relay server with one relay pool endpoint.

Important APIs/functions: `httpStatusEnhanceYourCalm` and `poolHandler`.

Control flow: each loop copies the relay URL, refreshes its host from the current NAT mapping, POSTs `{"url": ...}` to the pool, reads the response, and reacts by status code. On success it parses `evictionIn` and sleeps for 80 percent of that duration before rejoining. Server errors, bad requests, rate limiting, and unexpected statuses sleep one minute. Unauthorized logs and aborts permanently.

State and persistence: no durable state; membership is maintained by periodic HTTP registration. It uses the package `httpClient`, which may have TLS client cert and local address binding configured by `main.go`.

Dependencies/integration: integrates with `strelaypoolsrv` registration API and NAT mapping state.

Risks and test signals: URL host is recalculated each registration, which handles changing external NAT addresses. Unexpected success response JSON falls through to a one-hour sleep, which may delay rejoin. No tests cover retry/backoff behavior or response parsing.
