# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/doclient

Tiny rc helper for setting up a PPP client-side alternate network namespace.

Behavior:
- Binds `#I2` at `/net.alt2`.
- Starts connection server `ndb/cs -x .alt2`.

Integration points:
- Companion script for PPP testing/demo setups using alternate Plan 9 IP stacks.
