# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/db.c

`db.c` implements DHCP lease binding storage and allocation.

Key behavior:
- Lease files live under `binddir` (`/lib/ndb/dhcp` by default), named by IP address.
- `tohex` and `toid` convert client identifiers to printable strings.
- `syncbinding` lock-opens a lease file, rereads if qid changed, and lets the file win over cache.
- `initbinding` pre-populates binding cache for configured ranges.
- `iptobinding` finds/creates cached bindings by IP.
- `idtobinding` prefers previous matching bindings, then oldest expired/offered-free bindings on the requester’s network, optionally ICMP-probing candidates.
- `mkoffer`, `idtooffer`, `commitbinding`, and `releasebinding` implement offer/lease lifecycle.

Important dependencies:
- Uses global `now`, `minlease`, `blog`, `binddir`, and `icmpecho`.
- Uses `samenet` with `Info` network fields.

Notable risks/quirks:
- Uses exclusive lease files as a distributed coordination mechanism among servers.
- If lock cannot be acquired, it assumes someone else is using the binding.
