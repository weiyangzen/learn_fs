# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/pf_key_v2.c

This file is isakmpd’s OpenBSD PF_KEY v2 integration layer. It opens the kernel PF_KEY socket, constructs and parses PF_KEY messages, installs/deletes kernel SAs and flows, handles ACQUIRE and EXPIRE notifications, and creates dynamic on-demand configuration entries.

Major internal structures:
- `struct pf_key_v2_node`: one PF_KEY message segment/extension with type, size, flags, and ownership marker.
- `TAILQ_HEAD(pf_key_v2_msg, pf_key_v2_node)`: message container used for scatter/gather `writev(2)` and parsed incoming extensions.
- `PF_KEY_V2_ROUND()` and `PF_KEY_V2_CHUNK`: enforce PF_KEY 64-bit extension alignment.

Core PF_KEY message helpers:
- `pf_key_v2_msg_new()`, `pf_key_v2_msg_add()`, `pf_key_v2_msg_free()`: build and destroy segment queues.
- `pf_key_v2_seq()`: monotonically allocates request sequence IDs.
- `pf_key_v2_write()`: writes a queued PF_KEY message with version, pid, sequence, and computed length.
- `pf_key_v2_read()`: reads one PF_KEY packet, parses extensions, and filters by sequence/pid for synchronous replies.
- `pf_key_v2_call()`: write request and wait for matching reply.
- `pf_key_v2_find_ext()`: returns a parsed extension node by extension type.

Public operations:
- `pf_key_v2_open()`: opens `socket(PF_KEY, SOCK_RAW, PF_KEY_V2)` and registers for ESP, AH, and IPCOMP notifications.
- `pf_key_v2_get_spi()`: sends `SADB_GETSPI` for ESP/AH/IPCOMP and returns allocated SPI/CPI bytes.
- `pf_key_v2_get_kernel_sa()`: fetches kernel SA state with `SADB_GET` into a static `struct sa_kinfo`.
- `pf_key_v2_set_spi()`: installs or updates an SA, including algorithm mapping, replay window, lifetimes, UDP encapsulation, keys, identities, flow selectors, pf tag, and ipsec interface metadata.
- `pf_key_v2_enable_sa()` / `pf_key_v2_disable_sa()`: add or remove bidirectional policy flows for an established phase 2 SA.
- `pf_key_v2_delete_spi()`: deletes one kernel SA and removes dynamic configuration if appropriate.
- `pf_key_v2_connection_check()`: starts an exchange for dynamically created on-demand connections.
- `pf_key_v2_handler()`: main-loop readable-fd handler for asynchronous PF_KEY notifications.
- `pf_key_v2_group_spis()`: groups multiple protocol SAs via OpenBSD `SADB_X_GRPSPIS`.

Important control flow:
- Outbound install path: negotiated `struct sa` and `struct proto` data are translated into PF_KEY `SADB_ADD`/`SADB_UPDATE`, key extensions, address extensions, identity extensions, flow selectors, optional UDP encapsulation, optional tag, and optional interface extension.
- Flow path: `pf_key_v2_flow()` emits OpenBSD `SADB_X_ADDFLOW` or `SADB_X_DELFLOW` messages with source/destination flow, masks, transport protocol, identity extensions, and direction.
- Expire path: `pf_key_v2_notify()` dispatches `SADB_EXPIRE` to `pf_key_v2_expire()`, which looks up the matching isakmpd SA, may renegotiate on soft/hard lifetime events, and frees hard-expired SAs.
- Acquire path: `pf_key_v2_acquire()` handles kernel `SADB_ACQUIRE`, asks the kernel for matching policy, derives phase 1 peer, phase 2 local/remote IDs, defaults suites, dynamic config sections, reference counts, and then records/checks the passive connection.

Dependencies:
- Kernel PF_KEY headers: `<net/pfkeyv2.h>`, `<netinet/ip_ipsp.h>`.
- isakmpd subsystems: `conf`, `connection`, `exchange`, `ipsec`, `sa`, `timer`, `transport`, `ui`, `util`, `policy`, `udp_encap`.
- Uses OpenBSD-specific PF_KEY extensions such as flows, policies, tags, UDP encapsulation, ipsec interfaces, and grouped SPIs.

Risk notes:
- The file relies on many OpenBSD PF_KEY extension layouts and is not portable PF_KEY-only code.
- `pf_key_v2_read()` queues unexpected synchronous messages by scheduling immediate `pf_key_v2_notify` timer callbacks, so timer processing is part of PF_KEY notification delivery.
- `pf_key_v2_get_kernel_sa()` appears to assign `ssa = (struct sadb_sa *)ext` rather than `ext->seg` after finding `SADB_EXT_SA`; that is a suspicious cast in a state-extraction path.
- Dynamic config creation in `pf_key_v2_acquire()` is large and branch-heavy; failures must unwind allocated IDs, peer names, config transactions, and message objects.
- Identity conversion only supports FQDN/user FQDN and address/prefix forms; ranges, ASN.1 names, and key IDs are intentionally not converted for PF_KEY identity extensions.
