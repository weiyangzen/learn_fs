# File Research: sources/os/bsd/openbsd-src/sbin/unwind/dns64_synth.h

Header for the OpenBSD frontend DNS64 synthesis helper.

Exports:
- `dns64_synth_aaaa_data(const struct ub_packed_rrset_key *, const struct packed_rrset_data *, struct ub_packed_rrset_key *, struct packed_rrset_data **, struct regional *)`

Dependencies:
- The declaration relies on Unbound rrset and regional allocator types being visible from including translation units.

Role in group:
- Provides the local synthesis API used by `frontend.c` without exposing the helper internals.
