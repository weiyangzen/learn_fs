# File Research: sources/os/plan9/9front/sys/src/9/ip/devip.c

Implements the Plan 9 `#I` IP device filesystem. It exposes protocols, conversations, ARP, routes, logs, NDB data, and per-conversation control/data/status files through Qids.

Key responsibilities:
- Creates and attaches per-device `Fs` IP stacks in `ipattach()`.
- Generates the virtual directory tree through `ipgen()`, `ip1gen()`, `ip2gen()`, and `ip3gen()`.
- Implements open/read/write/stat/wstat/close for IP device files.
- Clones protocol conversations through `Fsprotoclone()`.
- Provides generic protocol control handling: `connect`, `announce`, `bind`, `ttl`, `tos`, multicast controls, and protocol-specific controls.
- Implements standard local/remote address and port parsing helpers for protocols.
- Maintains small per-stack NDB content.

Exposed namespace shape:
- Top-level files include `arp`, `bootp`, `ndb`, `iproute`, `ipselftab`, and `log`.
- Each protocol directory exposes `clone`, `stats`, optional `trans`, and conversation directories.
- Each conversation exposes `ctl`, `data`, `err`, `listen`, `local`, `remote`, `status`, and optional `snoop`.

Important implementation details:
- Qid path bits encode type, conversation index, and protocol index.
- `IPaux` attached to channels records the attaching user and a route tag.
- Conversation permissions are owner-sensitive; first open claims owner and resets default permissions.
- `closeconv()` tears down incoming calls, multicast memberships, protocol state, and returns the conversation to idle.
- `setlport()` picks restricted ports from 600-1023 or random unrestricted ports from 32768-65535.
- `Fsnewcall()` creates accepted inbound calls and queues them on a listener’s `incall` list.

Dependencies and integration:
- Initializes `ip_init`, `arpinit`, `netloginit`, and all registered `ipprotoinit[]`.
- Protocol modules register with `Fsproto()`.
- Uses helper APIs from routing, ARP, IP interface, multicast, and NAT translation code.

Research notes:
- This is the main user/kernel control plane for the networking stack.
- Protocol implementations rely on `devip.c` for common conversation lifecycle and address parsing.
- `scalednconv()` scales default conversation count on larger CPU servers.
