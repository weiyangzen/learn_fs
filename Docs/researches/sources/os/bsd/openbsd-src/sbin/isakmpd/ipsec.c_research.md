# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ipsec.c

IPsec DOI implementation for `isakmpd`.

It registers the IPsec DOI dispatch table, defines Quick Mode and New Group Mode payload scripts, validates DOI-specific exchanges/protocols/transforms/attributes, decodes negotiated IKE/IPsec attributes, and routes phase-1/phase-2 exchanges to main mode, aggressive mode, transaction mode, informational mode, and quick mode handlers.

The phase-1 finalizer transfers negotiated hash/PRF/SKEYID material into the ISAKMP SA, installs lifetime timers, and starts NAT-T keepalives. The phase-2 finalizer builds traffic selectors from ID payloads, applies optional config-driven PF tags and interface bindings, installs inbound/outbound SPIs through PF_KEY, groups bundled protocol SPIs, enables flows unless acquire-only/interface/on-demand policy says not to, and marks older ready SAs with the same flow as replaced.

It also owns IPsec selector/ID helpers: parsing configured address/subnet IDs, building ISAKMP ID payloads, cloning and rendering IDs, applying configured `NAT-ID`, deriving transport-mode NAT-T flows from the ISAKMP SA addresses, and computing ESP/AH key material lengths. Informational handling processes DELETE payloads, authenticated INITIAL-CONTACT notifications, HASH payload insertion/finalization, and protected informational pre/post hooks.

Notable constraints: only identity-only situations are accepted; many legacy/optional ID and attribute forms are explicitly unsupported; phase-1 default lifetime is 8 hours; INITIAL-CONTACT is rejected in aggressive mode or when unauthenticated/unprotected; DELETE payloads enforce protocol-specific SPI sizes and payload-length bounds before deletion.
