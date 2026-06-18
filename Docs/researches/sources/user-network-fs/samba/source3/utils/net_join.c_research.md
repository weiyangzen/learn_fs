# sources/user-network-fs/samba/source3/utils/net_join.c

## Purpose
This file implements the generic `net join` command. It chooses between Active Directory join and RPC join behavior and provides usage text.

## Important APIs, Types, And Control Flow
`net_join_usage()` prints valid methods and common flags. `net_join()` handles `HELP`, warns about member options via `net_warn_member_options()`, probes ADS suitability with `net_ads_check_our_domain()`, tries `net_ads_join()`, and falls back to `net_rpc_join()` when ADS probing or joining fails.

## State And Persistence
This file does not directly persist data, but the delegated ADS or RPC join modifies domain membership state, secrets, and machine-account configuration. It forwards the same arguments and `struct net_context` to the selected implementation.

## Dependencies And Integration Points
It depends on `utils/net.h` and externally implemented ADS/RPC join functions declared in `net_proto.h`. It is the user-facing auto-detection layer for `net ads join` versus `net rpc join`.

## Risks And Test Signals
The fallback path can mask ADS-specific failures by attempting RPC after an ADS join error. Tests should verify `HELP`, ADS-success short-circuit, ADS-failure fallback messaging, RPC-only behavior when ADS domain check fails, and option forwarding to both join backends.
