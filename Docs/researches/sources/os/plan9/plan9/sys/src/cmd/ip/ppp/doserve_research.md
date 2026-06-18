# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/doserve

Tiny rc helper for setting up a PPP server-side alternate network namespace.

Behavior:
- Binds `#I1` at `/net.alt`.
- Starts `ndb/cs -x .alt`.
- Starts `aux/listen` with `/rc/bin/service` on `/net.alt/tcp`.

Integration points:
- Companion script for PPP service/testing setups.
