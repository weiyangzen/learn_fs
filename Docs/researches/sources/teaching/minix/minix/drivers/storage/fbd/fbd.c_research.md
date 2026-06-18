# File Research: sources/teaching/minix/minix/drivers/storage/fbd/fbd.c

## Purpose
Implements FBD, a fault-injection proxy block driver that forwards requests to another block driver and applies configured rules to reads/writes.

## Main Flow
Fresh initialization parses `label` and `minor` options, resolves the target driver endpoint through DS, allocates a scratch buffer, seeds random generation, and announces as a blockdriver service.

Open, close, and non-FBD ioctls are forwarded to the target block driver. FBD-specific ioctls are handled through `rule_ctl()`.

## Key Behavior
- Uses `BLOCKDRIVER_TYPE_OTHER`, so it does not perform partition handling.
- `fbd_transfer()` totals the request size, finds matching rules, applies pre hooks, chooses direct forwarding or copy interposition, then applies post hooks.
- Direct forwarding creates indirect grants for the caller’s iovec grants and sends a normal blockdriver gather/scatter request to the real driver.
- Copy forwarding copies writes into local memory, applies I/O hooks, forwards local grants, applies read corruption after the lower read completes, and copies successful read bytes back to the caller.
- Allocates a larger temporary buffer dynamically when a request exceeds the static `BUF_SIZE`.

## Integration Notes
Requires a target driver label/minor at startup. Uses DS endpoint lookup, MINIX grant APIs, safecopy vectors, and blockdriver messages. Rule semantics are provided by `rule.c` and `action.c`.

## Risks
Grant lifetime and revocation are central. Copy interposition must preserve iovec chunking and partial read semantics. The driver panics on unexpected target protocol replies, so lower-driver protocol violations are fatal.
