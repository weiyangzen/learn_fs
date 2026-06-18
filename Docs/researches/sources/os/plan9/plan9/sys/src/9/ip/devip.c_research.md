# File Research: sources/os/plan9/plan9/sys/src/9/ip/devip.c

Implements the Plan 9 `#I` IP device namespace and the generic filesystem-facing control plane for IP protocols.

Key responsibilities:
- Builds qid layout for top-level files (`arp`, `bootp`, `ndb`, `iproute`, `ipselftab`, `log`), protocol directories, conversation directories, and per-conversation files (`ctl`, `data`, `err`, `listen`, `local`, `remote`, `status`, `snoop`).
- Lazily creates per-device `Fs` stacks in `ipgetfs`, initializes IP, ARP, logging, and registered protocol initializers.
- Handles attach, walk, stat, open, close, read, block read, write, block write, and wstat for the IP namespace.
- Owns conversation cloning through `Fsprotoclone`, including queue creation/reopen, owner/permission initialization, route cache reset, local/remote address defaults, TTL/TOS defaults, and per-protocol create hooks.
- Provides shared connect/announce/bind helpers: `Fsstdconnect`, `Fsstdannounce`, `Fsstdbind`, local/remote address parsing, local port selection, restricted port handling, and unique tuple checks.
- Implements listen queue handling through `Fsnewcall` and `listen` file opens.
- Routes ctl commands such as `connect`, `announce`, `bind`, `ttl`, `tos`, `ignoreadvice`, multicast add/remove, and `maxfragsize`, with fallback to protocol-specific ctl handlers.
- Supports `ndb` writes with version/mtime tracking and route tags via `IPaux`.

Notable design:
- Protocols register a `Proto` with callbacks and conversation limits through `Fsproto`.
- `Fsrcvpcol` routes inbound packets to `ipmux` when installed, otherwise directly to the IP protocol table.
- Conversation lifecycle is reference-counted by opens; last close resets owner, permissions, multicast memberships, protocol state, and queues.
