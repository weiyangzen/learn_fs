# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/authzone.h

Header for locally hosted authoritative zones used by the iterator and downstream answer path.

Major structures:
- `struct auth_zones`: shared auth-zone container with zone tree, transfer tree, downstream flag, RPZ linked-list head, and RPZ lock.
- `struct auth_zone`: zone identity, lock, authoritative data tree, zonefile/fallback flags, slave/upstream/downstream flags, ZONEMD settings, RPZ pointer, online ZONEMD callback state, delete state, and RPZ list links.
- `struct auth_data`: one owner name and linked rrsets.
- `struct auth_rrset`: typed authoritative RRset data.
- `struct auth_xfer`: zone-transfer coordinator with next-probe, SOA probe, transfer tasks, NOTIFY state, allowed-notify list, current serial/timers, and lease/expiry state.
- `struct auth_nextprobe`, `auth_probe`, and `auth_transfer`: worker-owned event-loop tasks for scheduled refresh, SOA probes, and AXFR/IXFR/HTTP transfer.
- `struct auth_master`, `auth_addr`, and `auth_chunk`: upstream master config, resolved addresses, and transfer data chunks.

Zone management API:
- Create, configure, cleanup, delete, and memory-account auth zones.
- Apply config and read/write zonefiles.
- Find zones/transfer records by name/class.
- Create zones and transfer records under locks.
- Configure zonefile and fallback behavior.
- Determine whether fallback to normal recursion is allowed.

Answering/query integration:
- `auth_zones_lookup()` answers iterator-side queries from local authoritative data or signals fallback.
- `auth_zones_downstream_answer()` creates downstream authoritative answers for clients.
- `auth_zones_find_zone()` finds closest enclosing local auth zone.

Transfer/notify API:
- Processes NOTIFY messages, parses SOA serials, starts probe sequences, compares RFC1982 serials, sets masters, and exposes probe/transfer callbacks.
- Supports UDP SOA probe callbacks, TCP/HTTP transfer callbacks, timers, and mesh callbacks for resolving master hostnames.
- Provides pickup/disown/delete helpers so transfer tasks are attached to the correct worker event loop.

ZONEMD:
- Defines supported ZONEMD scheme and SHA-384/SHA-512 algorithm constants.
- Declares hash generation, digest checking, full verification, DNSKEY lookup callback, and worker pickup for online verification.

RPZ role:
- Auth zones can contain RPZ data and are linked under `auth_zones.rpz_first`.
- Response-IP processing uses this RPZ list to apply policy based on returned IPs.

Filesystem/storage relevance:
- Not filesystem code, but it manages persistent zonefile paths and locally stored authoritative DNS data with rbtrees, locks, event-loop transfer tasks, and optional write-back.
