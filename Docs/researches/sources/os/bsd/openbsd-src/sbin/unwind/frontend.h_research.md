# File Research: sources/os/bsd/openbsd-src/sbin/unwind/frontend.h

Public declarations and shared frontend data structures for `unwind`.

Definitions:
- `HAVE_IPV4`, `HAVE_IPV6` bit flags.
- `struct trust_anchor`: TAILQ node containing a DNSKEY trust anchor string.
- `struct imsg_rdns_proposal`: interface index, source, and routing DNS sockaddr for resolver updates.
- `struct dns64_prefix`: IPv6 prefix, prefix length, and flags.

Exports:
- frontend lifecycle and imsg dispatch/compose functions.
- `ip_port()` formatting helper.
- trust anchor helpers: `add_new_ta()`, `free_tas()`, `merge_tas()`.

Role in group:
- Shared contract between frontend implementation, resolver/main messaging, and DNS64 synthesis helpers.
