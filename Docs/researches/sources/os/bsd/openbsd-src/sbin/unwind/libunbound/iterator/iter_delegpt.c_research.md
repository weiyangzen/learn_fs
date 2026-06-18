# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_delegpt.c

Implementation of Unbound delegation points: NS names, target addresses, and selection lists for iterative resolution.

Allocation modes:
- Regional allocation for per-query delegation points.
- Malloc-backed `_mlc` variants for persistent configuration objects such as forward zones.

Core behavior:
- Create/copy/set delegation point name.
- Add NS names, target addresses, A rrsets, AAAA rrsets, and generic NS/A/AAAA rrsets.
- Avoid duplicate NS names and duplicate target addresses.
- Track whether NS names have usable A/AAAA data.
- Track bogus and lame/parent-side information.
- Maintain `target_list`, `usable_list`, and `result_list`.
- Build delegation points from DNS messages by finding NS rrsets in authority or answer sections and collecting relevant glue from answer/additional sections.
- Mark negative A/AAAA lookups for nameservers.
- Mark nameservers resolved when IPv4 or IPv6 is unavailable.
- Log delegation point summary and details.
- Compute memory usage.

Important semantics:
- `delegpt_add_target()` only accepts target addresses whose owner name matches an existing NS in the delegation point.
- `delegpt_add_addr()` can add address-only targets, used by configured forwarders.
- `delegpt_from_message()` treats a message as useful if it can construct a delegation point; it does not fully validate referral semantics.
- Parent-side/lame addresses are dispreferred but kept for fallback.

Role in group:
- Foundational data model used by iterator and forward-zone code for upstream server selection.
