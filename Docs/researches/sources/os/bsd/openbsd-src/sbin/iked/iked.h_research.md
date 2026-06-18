# File Research: sources/os/bsd/openbsd-src/sbin/iked/iked.h

`iked.h` is the central shared header for daemon structures, constants, macros, and cross-module prototypes. It defines common IKE headers, imsg/event wrappers, control socket state, runtime SA/policy/flow/Child SA/user/RADIUS structures, crypto wrapper state, EAP state, message parse state, privsep process state, daemon global state, and function declarations for most iked modules.

Core runtime models are defined here: `iked_policy` for configured connection policy, `iked_sa` for live IKE SA state, `iked_childsa` for kernel IPsec SA state, `iked_flow` for traffic selectors/flows, `iked_message` for parsed inbound/outbound message state, and `iked` for daemon-global process state.

The header also defines request/state flag bits, timer constants, retransmit limits, fragmentation limits, MOBIKE flags, NAT-T mode, static daemon configuration, stats counters, and RB/TAILQ/SIMPLEQ container types. Many modules depend on these shared layouts, making this a high-coupling ABI within the daemon.

Security-relevant surfaces exposed here include certificate/auth buffers, derived key buffers, EAP/MSCHAP state, RADIUS secrets/requests, PF_KEY and socket descriptors, privsep process IDs, imsg size-check macros, and global mutable daemon settings.

Because this header declares most module interfaces, changes here have broad blast radius across CA, config, control, crypto, DH, EAP, IKEv2, PF_KEY, policy, RADIUS, timer, proc, util, OCSP, parser, and print code.
