## sources/sync-backup/syncthing/lib/discover/global_test.go

Purpose: Tests global discovery URL option parsing, HTTP/HTTPS security behavior, lookup, timeout, server identity validation, and announcements.

Important APIs/types/functions: `TestParseOptions`, `TestGlobalOverHTTP`, `TestGlobalOverHTTPS`, `TestGlobalAnnounce`, `testLookup`, `fakeDiscoveryServer`, and `fakeAddressLister`.

Control flow: Tests construct local HTTP/TLS servers, exercise `NewGlobal` with different query options, perform lookups, validate error/success modes, start discovery service for announcement, and wait for error state to clear.

State and persistence: In-memory fake server captures POST body. No disk persistence.

Dependencies and integration points: Uses `tlsutil.NewCertificateInMemory`, registry, events noop logger, and real HTTP servers.

Risks: Timeout test is skipped in short mode and depends on request timeout behavior. Fake server returns an intentionally odd address string, so assertions are tightly coupled to current parser permissiveness.

Test signals: Strong security and protocol behavior coverage for global discovery client.
