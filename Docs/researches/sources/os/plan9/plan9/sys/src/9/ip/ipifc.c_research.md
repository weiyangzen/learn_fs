# File Research: sources/os/plan9/plan9/sys/src/9/ip/ipifc.c

Implements the `ipifc` protocol: interface binding, address management, local self-cache, multicast, and IPv6 autoconfiguration controls.

Key responsibilities:
- Maintains registered `Medium` implementations and looks them up by name.
- `ipifcbind` attaches an interface conversation to a medium, calls medium bind, initializes MTUs/router-advertisement defaults, increments interface generation, and reopens queues.
- `ipifcunbind` removes logical interfaces, routes, self-cache entries, medium bindings, and closes queues.
- Reports interface state and local self-cache links through `status`/`local`.
- `ipifckick` passes packets written to an interface’s `data` file to the medium `pktin` hook.
- `ipifcadd` parses address/mask/remote/MTU/proxy arguments, adds logical interfaces, local routes, self-cache entries, broadcast/multicast entries, IPv6 solicited-node multicast entries, and optional duplicate-address-detection solicitation.
- `ipifcrem` and `ipifcremlifc` remove logical addresses and their routes/self-cache links.
- Propagates route additions/removals to media that provide route hooks.
- Supports ctl commands: `add`, `try`, `remove`, `unbind`, `joinmulti`, `leavemulti`, `mtu`, `reassemble`, `iprouting`, `add6`, and `ra6`.
- Owns `Ipselftab`, used by `ipforme`, `iptentative`, `ipselftabread`, and route/interface selection.
- Selects local source addresses with IPv4/IPv6 scope and preferred-lifetime logic in `findlocalip`.
- Handles multicast membership records per conversation and maps them onto interface self-cache entries.
- Registers proxy addresses for ARP/ND on appropriate interfaces.
- `ipifcadd6` builds an IPv6 address from a prefix and medium-provided MAC-derived interface identifier.

Notable design:
- Removed self-cache links are delayed before free to reduce lock contention with readers.
- A null/unspecified address in self-cache enables accept-all behavior.
