# File Research: sources/os/plan9/9front/sys/src/cmd/mount.c

Plan 9 `mount` command implementation.

Behavior:
- Parses mount options: after/before/create/cache flags, key pattern, no-auth, become-none/no-auth, and quiet mode.
- Opens the supplied service endpoint read-write.
- Optionally switches process user to `none`.
- Authenticated path calls `fauth` and `auth_proxy` with `proto=p9any role=client`, then mounts with the returned auth fd.
- No-auth path mounts directly with auth fd `-1`.
- Reports errors unless quiet mode is enabled.

Important interactions:
- Uses Plan 9 auth library (`auth_proxy`, `amount_getkey`) and the kernel `mount` call.
- Supports optional attach spec (`aname`) as the third positional argument.

Notable quirks:
- If `fauth` succeeds but `auth_proxy` fails, it logs the auth failure but still attempts the mount with the auth fd.
- `-N` implies `-n` and tries to mount as user `none`.
