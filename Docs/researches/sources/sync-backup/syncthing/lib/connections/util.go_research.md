## sources/sync-backup/syncthing/lib/connections/util.go

Purpose: Shared URL/address helpers for connection transports and discovery advertisement.

Important APIs/types/functions: `fixupPort`, `getURLsForAllAdaptersIfUnspecified`, `getHostPortsForAllAdapters`, `resolve`, `maybeReplacePort`, and `portMappingURIs`.

Control flow: `fixupPort` fills default ports for missing or empty URL ports. Adapter expansion resolves a listen URI, checks for unspecified address and nonzero port, enumerates interface networks, and builds host:port URLs for private/link-local addresses. `maybeReplacePort` substitutes actual bound port for configured zero port. `portMappingURIs` converts NAT external addresses into listener URLs and adds zero-IP variants for DMZ-like cases.

State and persistence: Stateless helpers, except for current interface address lookup.

Dependencies and integration points: Used by TCP/QUIC listeners and dialers; depends on `nat` and `osutil`.

Risks: URL parsing and IPv6 bracket handling are subtle. Interface enumeration failures silently suppress LAN address expansion. Mutating `addr.IP` while building zero-IP NAT variants relies on value semantics of loop variables.

Test signals: Connection tests cover `fixupPort`; listener behavior indirectly covers advertisement helpers.
