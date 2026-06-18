## sources/sync-backup/syncthing/lib/discover/global.go

Purpose: Implements global discovery client for announcing local addresses to HTTPS discovery servers and querying remote device addresses.

Important APIs/types/functions: `globalClient`, `httpClient`, `announcement`, `serverOptions`, `lookupError`, `NewGlobal`, `Lookup`, `Serve`, `sendAnnouncement`, `parseOptions`, `queryBool`, `idCheckingHTTPClient`, `errorHolder`, `contextClient`, identity helpers, and `http2EnabledTransport`.

Control flow: `NewGlobal` parses server options, builds separate announce and query HTTP clients, optionally wraps them with discovery-server device ID verification, and sets initial error when announcement is required. `Lookup` adds `device` query parameter, performs GET, handles non-200 and `Retry-After`, and decodes addresses. `Serve` debounces listen-address-change events and calls `sendAnnouncement`; repeated flip-flopping suppresses endless resets. `sendAnnouncement` marshals sanitized external addresses, POSTs them, follows `Retry-After` or `Reannounce-After`, and updates error state.

State and persistence: Holds server URL, address lister, clients, no-announce/no-lookup flags, and mutex-protected current error. No persistent cache; manager wraps it with cache.

Dependencies and integration points: Uses TLS cert identity, dialer proxy/reuse-port dialing, events `ListenAddressesChanged`, registry, HTTP/2 transport, and relay address sanitization from local discovery.

Risks: TLS `InsecureSkipVerify` is enabled for `?insecure` or explicit ID mode, with manual device ID verification only when `id` is supplied. HTTP is allowed only for insecure no-announce lookups. Timer reset/debounce logic must avoid missed announcements and permanent flip-flop suppression.

Test signals: `global_test.go` covers option parsing, HTTP restrictions/lookups, HTTPS certificate modes, ID verification, lookup timeout, and successful announcement.
