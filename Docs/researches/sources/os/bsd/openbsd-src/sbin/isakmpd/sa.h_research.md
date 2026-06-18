# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/sa.h

This header defines the central isakmpd SA and protocol structures.

Key structures:
- `struct proto`: one protocol proposal/selection inside an SA, including protocol number, SPIs for outgoing/incoming directions, chosen transform, transform ID, DOI-specific data, and stored proposal transform attributes.
- `struct proto_attr`: stored transform attribute blob used for responder-selection validation.
- `struct sa`: phase 1 or phase 2 security association with name, transport, cookies, message ID, protocol list, DOI, keystate, IDs, initiator flag, policy data, cert/key material, lifetimes, kernel acquire sequence, timers, NAT-T keepalive timer, DPD state, pf tag, and optional interface unit.
- `struct sa_kinfo`: kernel SA telemetry used mostly by DPD, including lifetimes, byte/allocation counters, addresses, SPI, UDP encapsulation port, and replay window.

Flags:
- Readiness and lifecycle: `SA_FLAG_READY`, `SA_FLAG_STAYALIVE`, `SA_FLAG_ONDEMAND`, `SA_FLAG_REPLACED`, `SA_FLAG_FADING`, `SA_FLAG_ACTIVE_ONLY`.
- Feature flags: `SA_FLAG_IKECFG`, `SA_FLAG_DPD`, `SA_FLAG_NAT_T_ENABLE`, `SA_FLAG_NAT_T_KEEPALIVE`, `SA_FLAG_IFACE`.

Exported APIs:
- SA lifecycle, lookup, reporting, transform add/free, replacement, expiration setup, and flag parsing.

Integration:
- This is a shared contract across exchange negotiation, IPsec DOI code, PF_KEY installation, NAT traversal, DPD, policy, and transport handling.
