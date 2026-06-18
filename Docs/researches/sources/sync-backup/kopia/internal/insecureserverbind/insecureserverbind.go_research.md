# sources/sync-backup/kopia/internal/insecureserverbind/insecureserverbind.go

Purpose: prevents unauthenticated insecure Kopia servers from binding to public network interfaces unless an explicit dangerous escape hatch is set.

Important APIs/types/functions: `AllowDangerousUnauthenticatedNetworkFlag`, `AllowDangerousUnauthenticatedNetworkFlagHelp`, `ErrDisallowedPublicBind`, `RestrictionApplies`, `ValidateListenAddressIfRestricted`, `ValidateListenerAddrIfRestricted`, `ParseListenHost`, `ValidateListenAddressFlag`, and `ValidateListenerAddr`.

Control flow: restriction applies only when the server is insecure, has no password, and the dangerous flag is not set. Address validation strips leading HTTP/HTTPS, treats `unix:` as safe, parses hostnames, accepts empty only for Unix sockets, accepts `localhost` and loopback IPs, and rejects public IPs, wildcard binds, and non-localhost hostnames. Listener validation accepts Unix listeners and loopback TCP addresses after binding.

State/persistence behavior: no state is stored. The important behavioral state is CLI flag configuration and bound listener address.

Dependencies/integration: integrates with server startup and CLI flag handling. Uses `net`, `net/url`, and wrapped errors so callers can detect `ErrDisallowedPublicBind`.

Risks/test signals: DNS names other than literal `localhost` are rejected even if they resolve locally, which is conservative. Unknown listener types are rejected unless their network string is `unix`.
