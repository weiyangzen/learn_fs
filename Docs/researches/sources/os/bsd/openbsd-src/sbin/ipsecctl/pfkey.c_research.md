# File Research: sources/os/bsd/openbsd-src/sbin/ipsecctl/pfkey.c

This file emits, receives, monitors, and partially parses PF_KEY V2 messages for `ipsecctl`.

Key responsibilities:
- Opens a raw `PF_KEY` socket.
- Builds PF_KEY messages for flow add/delete, SA add/delete, SA bundle grouping, flush, and promiscuous monitoring.
- Converts `struct ipsec_rule` objects into kernel SADB operations.
- Reads PF_KEY replies and propagates kernel errors.
- Parses SADB flow messages back into partial `struct ipsec_rule` objects.
- Implements live PF_KEY monitor mode.

Important functions:
- `pfkey_init()` opens the global PF_KEY socket.
- `pfkey_ipsec_establish()` dispatches `RULE_FLOW`, `RULE_SA`, and `RULE_BUNDLE` operations to the correct PF_KEY builder.
- `pfkey_flow()` constructs `SADB_X_ADDFLOW`/`SADB_X_DELFLOW` messages with flow type, protocol, src/dst flows, masks, optional local/peer addresses, and optional identities.
- `pfkey_sa()` constructs `SADB_ADD`/`SADB_DELETE` messages with SA, src/dst addresses, optional UDP encapsulation, and optional key extensions.
- `pfkey_sabundle()` constructs `SADB_X_GRPSPIS` messages for bundle relationships.
- `pfkey_reply()` reads a complete reply based on the message header length.
- `pfkey_parse()` parses selected SADB flow extensions into `struct ipsec_rule`.
- `pfkey_ipsec_flush()` sends `SADB_FLUSH`.
- `pfkey_monitor()` enables PF_KEY promiscuous mode and loops on `poll`.
- `pfkey_promisc()` enables promiscuous PF_KEY delivery.

Notable behavior:
- Message lengths are expressed in `PFKEYV2_CHUNK` units and extension payloads are rounded up to 8-byte alignment.
- IPv4 and IPv6 source/destination addresses and masks are encoded into `sockaddr_storage`.
- Port-specific masks use `0xffff` when source or destination ports are set.
- Flow identities are encoded as `SADB_EXT_IDENTITY_SRC` and `SADB_EXT_IDENTITY_DST`.
- Static SA algorithm mapping mirrors transform IDs from `parse.y`.
- UDP encapsulation sets `SADB_X_SAFLAGS_UDPENCAP` and adds `SADB_X_EXT_UDPENCAP`.
- `pfkey_reply()` treats `EEXIST` as non-fatal for no-data callers.
- Monitor mode pledges to `stdio` after setup.

Dependencies:
- Uses `ipsecctl.h` rule structures.
- Uses `pfkey.h` declarations.
- Requires OpenBSD PF_KEY V2, IPsec, `writev`, `poll`, and socket APIs.

Research notes:
- This is the kernel interface layer for `ipsecctl`.
- `pfkey_flow()` and `pfkey_sa()` are sensitive to structure sizes, alignment, and OpenBSD-specific SADB extension semantics.
