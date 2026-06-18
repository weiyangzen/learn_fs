# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/rpz.h

`rpz.h` declares the Response Policy Zone service interface and data structures. It defines RPZ trigger categories for QNAME, client-IP, response-IP, NSDNAME, NSIP, and invalid policy names, plus action categories for NXDOMAIN, NODATA, passthrough, drop, TCP-only, invalid, local-data, disabled override, no override, and CNAME override.

`struct rpz` is the policy container attached to a corresponding auth-zone and linked in configuration order under the auth-zones RPZ lock. It owns QNAME local zones, response-IP data, synthesized client-IP and NSIP address trees, NSDNAME local zones, optional taglist matching, action override state, optional CNAME override rrset, logging options, NXDOMAIN RA signaling, a regional allocator, and a disabled flag.

The header also exposes the synthesized client/NS IP storage records: `clientip_synthesized_rrset` wraps a regional allocator, address tree, and lock; each `clientip_synthesized_rr` has an address-tree node, item lock, action, and optional local-data RRset list.

The public API covers inserting/removing policy RRs from RPZ feed updates, worker-request QNAME/client-IP processing, iterator NSDNAME/NSIP processing, CNAME-chain QNAME processing, RPZ create/delete/clear/config/finish operations, enable/disable toggles, action conversion helpers between RPZ and response-IP/local behavior, action stringification, and memory accounting. Callers are expected to respect auth-zone and RPZ locking contracts documented in the struct comments.
