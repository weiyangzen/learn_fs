# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/cs.c

Implements the Plan 9 connection server `ndb/cs`, a small 9P service that translates dial strings into clone paths and addresses.

Key responsibilities:
- Serves a 9P tree containing directory `.` and file `cs`, mounted under the selected net mount point and also exposed through `/srv/cs...`.
- Tracks per-fid `Mfile` state: user, qid, current request fields (`net`, `host`, `serv`, `rem`), next network to try, and cached reply strings.
- Handles 9P requests: version, auth rejection, flush, attach, walk, open, read, write, clunk, stat, and permission-denied create/remove/wstat.
- Parses writes to `cs` as either owner-only control commands (`debug`, `ipv4`, `ipv6`, `add`, `refresh`), general `!` ndb queries, or dial strings split on `!`.
- On reads, lazily returns one reply segment at a time and performs more lookups as offsets advance.
- Builds a default network list by checking available `/net/<proto>/clone` files, and supports manual network additions.
- Tracks local IP interfaces, configured IPv4/IPv6 availability, DNS-usable addresses, and system name discovery.
- Resolves IP services through ndb `port` records and marks restricted TCP ports.
- Resolves hosts via DNS first for domains, then ndb, with fallback from non-domain attributes to domain names.
- Reorders IP results to prefer addresses on local interface networks.
- Translates IP results into dialable strings like `/net/tcp/clone ip!port`.
- Translates telco records similarly for the `telco` network.
- Spawns bounded slave processes around DNS lookups so slow DNS requests do not block the main 9P server.
- Mounts `/srv/dns...` into the net mount point on demand.
- Implements general tuple queries and `ipinfo` queries, including optional resolution of `@attr` values.

Important interactions:
- Uses libndb, DNS query helpers, Plan 9 network interface inspection, 9P fcall conversion, `/srv`, `/net`, `/net/ndb`, and `/dev/sysname`.
- Shares DNS and database behavior with other `ndb` files such as `dblookup.c`.

Notable quirks:
- Global database access is serialized by `dblock`.
- Active DNS slave count is capped at `Maxactive`.
- Unknown network names are passed through without host/service translation.
