# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_delegpt.h

Header defining Unbound delegation point structures and APIs.

Core structures:
- `struct delegpt`: delegated domain name, NS list, target/usable/result address lists, bogus flag, parent-side/fallback flags, upstream TCP/TLS flags, auth-zone marker, no-cache marker, allocation-mode marker.
- `struct delegpt_ns`: nameserver wire name, lookup counters, resolved/got4/got6 state, lame/parent-side state, TLS auth name, port.
- `struct delegpt_addr`: sockaddr target, attempt/selection RTT counters, bogus/lame/dnsseclame flags, TLS auth name, and list links.

API:
- Regional create/copy/name/add functions.
- Add NS/A/AAAA rrsets and parsed target addresses.
- Find NS or address.
- Count/log names and addresses.
- Move usable targets to result list.
- Count missing/total targets.
- Build from DNS message.
- Mark negative address lookups and IPv4/IPv6 unavailability.
- Malloc-backed create/free/add variants.
- Memory accounting and result-list helpers.

Role in group:
- Public contract for delegation point manipulation across iterator, hints, stubs, and forwards.
