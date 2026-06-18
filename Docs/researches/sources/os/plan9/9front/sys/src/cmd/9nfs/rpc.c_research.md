# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/rpc.c

RPC/XDR marshaling, unmarshaling, diagnostics, and common reply helpers for 9nfs daemons.

Key responsibilities:
- `rpcM2S()` decodes UDP-header-prefixed SunRPC messages into `Rpccall`.
- `rpcS2M()` serializes `Rpccall` replies/calls back into UDP-header-prefixed network buffers.
- `auth2unix()` decodes `AUTH_UNIX` credentials into `Authunix`.
- `string2S()` decodes counted XDR strings, NUL-terminates them, and interns them.
- `rpcprint()` and `showauth()` provide debug formatting.
- `garbage()` and `error()` set common RPC failure/result payloads.

Important behavior:
- IPv4 addresses are extracted from Plan 9 `Udphdr` IPv4-mapped address tails.
- XDR pointer fields are aliases into the original packet buffer, except strings interned by `string2S()`.
- Variable-length fields advance by 4-byte-rounded XDR sizes.
- `auth2unix()` skips surplus gids beyond the fixed local `gids` array.

Dependencies:
- Uses `rpc.h` constants/macros, Plan 9 UDP headers, `strstore()`, and logging helpers.

Notable risks:
- Decode macros do not perform local bounds checks on every individual field; callers rely on final byte-count validation.
- `string2S()` trusts the encoded length enough to allocate `n+1`.
