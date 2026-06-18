# File Research: sources/os/bsd/openbsd-src/sbin/slaacd/engine.c

Implements the `slaacd` engine process: the policy/state-machine half of IPv6 SLAAC. It receives interface facts and router advertisements from the frontend, derives address/default-route/RDNS proposals, tracks proposal lifetimes, and asks the privileged main process to configure or withdraw kernel state.

Major structures:
- `struct slaacd_iface`: per-interface state, flags, link-local address, SOII key, current MTU, RA list, and proposal lists.
- `struct radv`, `radv_prefix`, `radv_rdns`: parsed router advertisement state with lifetimes, prefixes, RDNSS servers, router preference, and MTU.
- `struct address_proposal`, `dfr_proposal`, `rdns_proposal`: pending/configured SLAAC outputs with timers, lifetimes, source router, interface ID, and state.

Process setup:
- `engine()` drops privileges to `_slaacd`, unveils `/` with no permissions, pledges `stdio recvfd`, initializes libevent, and waits for imsg links.
- After the main process passes the frontend IPC socket, the engine reduces pledge to `stdio`.
- Uses OpenBSD `imsg`, libevent timers, `LIST_HEAD` queues, and signal handlers.

Core imsg handling:
- From frontend: handles RA packets, interface removal, manual solicitation requests, address/route deletion notifications, duplicate-address notifications, RDNS reproposal, and control queries.
- From main: receives frontend IPC fd and interface-update messages.
- Sends configuration requests to main through `IMSG_CONFIGURE_ADDRESS`, `IMSG_WITHDRAW_ADDRESS`, `IMSG_CONFIGURE_DFR`, `IMSG_WITHDRAW_DFR`, and `IMSG_PROPOSE_RDNS`.

SLAAC state machines:
- Interface states: `IF_DOWN`, `IF_INIT`, `IF_BOUND`.
- Proposal states: `PROPOSAL_IF_DOWN`, `PROPOSAL_NOT_CONFIGURED`, `PROPOSAL_CONFIGURED`, `PROPOSAL_NEARLY_EXPIRED`, `PROPOSAL_WITHDRAWN`, `PROPOSAL_DUPLICATED`, `PROPOSAL_STALE`.
- `iface_state_transition()` sends router solicitations while initializing, stops probing after `MAX_RTR_SOLICITATIONS`, and marks proposals down/withdrawn as link state changes.
- Proposal transition functions compute timers from remaining lifetimes, request fresh solicitations near expiry, withdraw stale state, and handle duplicated addresses.

Router advertisement parsing:
- `parse_ra()` validates ICMPv6 RA type/code, link-local sender, option lengths, prefix length, MTU minimum, and RDNSS layout.
- Parses prefix information, RDNSS, MTU, router lifetime, reachable/retransmit time, managed/other flags, and router preference.
- Ignores unsupported ND options such as DNSSL, route info, redirected header, and link-layer address options.
- `debug_log_ra()` provides verbose RA decoding when built without `SMALL`.

Address generation:
- `gen_addr()` constructs an IPv6 address from the advertised prefix and either:
  - random IID for temporary addresses,
  - SHA-512 stable opaque IID using prefix, MAC, DAD counter, and SOII key,
  - link-local IID for non-SOII prefixes up to /64.
- Temporary address lifetimes implement RFC 8981 constants: 2-day valid, 1-day preferred, desync factor, and regeneration advance.
- Duplicate non-temporary addresses increment per-prefix DAD counters and regenerate SOII addresses.

Proposal updates:
- `update_iface_ra()` replaces old RAs from the same router, preserving DAD counters, then updates default route, address, and RDNS proposals.
- `update_iface_ra_prefix()` updates existing address proposals, creates stable and temporary proposals when allowed, removes disabled address kinds, and applies advertised MTU changes once.
- `update_iface_ra_dfr()` maps router lifetime into default-route proposals.
- `update_iface_ra_rdns()` aggregates RDNSS servers, truncating to `MAX_RDNS_COUNT`, and reproposes DNS via route proposals.

Resource/lifetime management:
- Explicit free helpers remove list entries, delete timers, and withdraw configured kernel state when needed.
- Timeout handlers transition configured proposals to nearly expired, stale, duplicated regeneration, or final free.
- `real_lifetime()` converts RA-relative lifetimes using monotonic time.

Filesystem/storage relevance:
- No filesystem implementation. It is OS network configuration infrastructure and uses OpenBSD daemon patterns relevant to privilege separation, route-socket mediated kernel state, and long-lived event/timer resource ownership.
