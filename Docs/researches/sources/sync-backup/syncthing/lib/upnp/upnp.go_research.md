# sources/sync-backup/syncthing/lib/upnp/upnp.go

Purpose: UPnP InternetGatewayDevice discovery, device-description parsing, service extraction, local address selection, and SOAP transport.

Important APIs and control flow: `init` registers `Discover` with NAT discovery. `Discover` enumerates running multicast interfaces, runs IPv6 IGDv2 discovery only when a global IPv6 address exists, then IPv4 IGDv2 and IGDv1 discovery, deduplicating results by ID. `discover` sends SSDP M-SEARCH over multicast, reads responses until timeout/context cancellation, and sends parsed IGD services to a result channel. `parseResponse` reads HTTP-like SSDP responses, validates ST, Location, and USN, fixes IPv6 link-local location hosts with zone-aware source addresses, downloads XML device descriptions, determines local IPv4 via interface or fallback UDP dial, marks IPv6 root devices, and extracts services. `getServiceDescriptions` selects IGDv1/v2 and IPv4/IPv6 service URNs. `replaceRawPath` normalizes relative/absolute control URLs. `soapRequestWithIP` builds SOAP HTTP POSTs with optional local bind address and returns response bytes even on HTTP errors. `interfaceHasGUAIPv6` screens IPv6 discovery.

State and persistence: discovery is in-memory; router state changes occur through IGDService methods.

Dependencies and integration: uses `netutil`, `dialer`, `osutil`, `build.Version`, `nat`, HTTP/XML, and logging. It is the NAT backend for UPnP.

Risks: network discovery is nondeterministic and router compatibility is fragile. `replaceRawPath` assumes non-empty relative path. Direct `http.Get` for device descriptions bypasses custom dialer/proxy settings. Tests cover XML and URL parsing only.
