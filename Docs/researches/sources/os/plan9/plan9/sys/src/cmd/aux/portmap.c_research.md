# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/portmap.c

SunRPC portmapper client. It connects to a host’s UDP portmap service and runs a requested portmapper procedure.

Commands:
- `null`
- `set prog vers proto port`
- `unset prog vers proto port`
- `getport prog vers proto`
- `dump` default

Core behavior:
- `portCall()` fills SunRPC portmapper program/version/procedure metadata.
- `tset()` and `tunset()` submit port mappings and print `rejected` on false response.
- `tgetport()` prints mapped port.
- `tdump()` prints all returned mappings as `prog vers proto port`.

Dependencies and integration:
- Uses `<thread.h>` and `<sunrpc.h>`.
- Uses generated/global `portProg` formatting/protocol metadata.
- Related to `nfsmount.c`, which embeds a smaller `getport()` helper.

Notable risks:
- No authentication or filtering; it exposes raw portmapper operations to the user.
- Numeric parsing uses `strtol()` without validating trailing garbage.
