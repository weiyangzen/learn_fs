# sources/sync-backup/kopia/internal/insecureserverbind/insecureserverbind_test.go

Purpose: validates insecure server bind restrictions across flag combinations, string listen addresses, bound listener addresses, Unix sockets, loopback IPs, and unknown address types.

Important APIs/types/functions: `RestrictionApplies`, `ValidateListenAddressIfRestricted`, `ValidateListenerAddrIfRestricted`, `ParseListenHost`, `ValidateListenAddressFlag`, `ValidateListenerAddr`, `ErrDisallowedPublicBind`, and `stubAddr`.

Control flow: parallel table tests check when validation is skipped or enforced. Address parsing covers HTTP, HTTPS, hostless binds, IPv4/IPv6 loopback, Unix socket forms, public IPs, and hostnames. Validation tests assert allowed loopback/Unix cases and ensure rejected cases wrap `ErrDisallowedPublicBind` and mention the escape-hatch flag.

State/persistence behavior: no durable state. The tests model startup configuration and post-listen socket validation.

Dependencies/integration: uses `net.TCPAddr`, `net.UnixAddr`, custom `net.Addr`, and `testify/require`. The suite is package-internal, so it covers unexported `ParseListenHost` behavior too.

Risks/test signals: tests intentionally reject `0.0.0.0`, hostless addresses, public test-net IPs, and arbitrary hostnames. They do not perform DNS resolution, matching the production conservative policy.
