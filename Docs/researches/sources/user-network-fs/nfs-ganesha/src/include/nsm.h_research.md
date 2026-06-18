# sources/user-network-fs/nfs-ganesha/src/include/nsm.h

## Purpose
This rpcgen header defines the Network Status Monitor protocol pieces used by Ganesha's NLM implementation to monitor client restarts and receive reboot notifications.

## Important APIs, Types, And Functions
Constants identify status monitor program/version/procedures: `SM_PROG`, `SM_VERS`, `SM_MON`, `SM_UNMON`, `SM_UNMON_ALL`, and `SM_NOTIFY`. Wire types include `res`, `sm_stat_res`, `sm_stat`, `my_id`, `mon_id`, `mon`, and `notify`. Ganesha-facing helpers are `nsm_monitor()`, `nsm_unmonitor()`, `nsm_unmonitor_all()`, and `nsm_notify()`. XDR declarations cover every wire type.

## Control Flow
The NLM layer asks NSM to monitor a host when lock state is established, unmonitor hosts when state is removed, unmonitor all during shutdown/reset, and process notify events carrying host and state values after a peer restarts. The `mon` structure combines monitored peer identity with callback identity and a private 16-byte token.

## State And Persistence
The header owns no runtime storage. It defines monitor identities and notification payloads. Actual monitor tables, host references, and restart-state persistence are implemented outside the header, tied to `state_nsm_client_t`.

## Dependencies And Integration Points
It includes `config.h`, `gsh_rpc.h`, and `sal_data.h`. It integrates NSM RPC/XDR data with SAL client state and the NLM reclaim/free-all paths that react to client restart notifications.

## Risks And Test Signals
Risks include host-name canonicalization mismatches, stale monitor records, private-token mismatch, and notification replay/order issues. Test signals include XDR round trips, monitor/unmonitor lifecycle tests, simulated `SM_NOTIFY` after client restart, unmonitor-all shutdown coverage, and NLM lock reclaim behavior during grace periods.
