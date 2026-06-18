# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/authnone.c

Defines the `authnone` backend for u9fs.

Behavior:
- `noneauth` returns an error saying no authentication is required.
- `noneattach` succeeds unconditionally.

Role: authentication policy where clients attach without an auth file exchange.
