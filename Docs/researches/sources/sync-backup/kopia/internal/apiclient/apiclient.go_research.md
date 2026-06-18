## sources/sync-backup/kopia/internal/apiclient/apiclient.go

Purpose: HTTP helper client for Kopia API server calls, including JSON/body handling, CSRF support, auth transport, logging, TLS pinning, and Unix-socket URLs.

Important APIs/types/functions: `KopiaAPIClient`, `Options`, `NewKopiaAPIClient`, `Get`, `Post`, `Put`, `Delete`, `FetchCSRFTokenForTesting`, `HTTPStatusError`, `requestReader`, `decodeResponse`, `basicAuthTransport`, and `loggingTransport`.

Control flow, state, and persistence: the client stores base URL, HTTP client/cookie jar, and an optional CSRF token. Requests choose binary or JSON request bodies, add CSRF and content type headers, run through configured transports, and decode bytes or JSON on HTTP 200. Non-200 responses become `HTTPStatusError`, optionally parsing an `error` JSON field. Unix URL schemes clone the transport and override dialing to a socket path.

Dependencies and integration points: integrates with server API tests and clients, `tlsutil.TransportTrustingSingleCertificate`, `timetrack`, and Go HTTP cookie management.

Risks and test signals: risks include nil/default transport type assertion assumptions for Unix sockets, greedy CSRF regex, response body consumed for error parsing, and lack of explicit timeout. No tests in this subset directly cover it.
