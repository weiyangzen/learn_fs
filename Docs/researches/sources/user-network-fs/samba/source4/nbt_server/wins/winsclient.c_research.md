# sources/user-network-fs/samba/source4/nbt_server/wins/winsclient.c

## Purpose

`winsclient.c` implements Samba nbtd's WINS client behavior for registering interface names with configured WINS servers and periodically refreshing those registrations. It is separate from the local WINS server path and acts on `nbtd_iface_name` records owned by local interfaces.

## Important APIs, Types, and Functions

The exported API is `nbtd_winsclient_register()`. Internal helpers include `wins_socket()` for selecting the primary name socket, `nbtd_wins_start_refresh_timer()`, `nbtd_wins_refresh()`, `nbtd_wins_refresh_handler()`, `nbtd_wins_register_handler()`, and `nbtd_wins_register_retry()`. State structs wrap `struct nbt_name_register_wins` and `struct nbt_name_refresh_wins` requests.

## Control Flow

Registration builds a WINS register request from the interface name, configured WINS server list, NBT port, local address list, flags, and TTL, then starts `nbt_name_register_wins_send()`. Timeout schedules a retry after `nbtd:wins_retry`; protocol errors mark the name conflicting or log failure; success marks the name active, stores the responding WINS server, records current time, and schedules refresh. Refresh uses the remembered WINS server, refreshes at `min(nbtd:max_refresh_time, ttl/2)`, and on timeout restarts registration from scratch.

## State and Persistence Behavior

State is in memory on `struct nbtd_iface_name`: `nb_flags`, `wins_server`, `registration_time`, and timers. There is no persistent database update in this file. The WINS server string returned by the client library is talloc-moved into the interface name after carefully stealing any old string into the temporary request state.

## Dependencies and Integration Points

It depends on nbtd interface structures, `winsserver.h`, tevent timers, generated NBT request structures, `cli-nbt`, service task event context, loadparm WINS configuration, and `nbtd_address_list()`. Startup and interface registration code invoke this when local names need WINS registration.

## Risks and Edge Cases

Timeout handling differs between register and refresh: register retries later, refresh immediately starts registration over. Non-timeout errors do not retry, which can leave a name inactive or stale until external registration is triggered. If no local addresses are available, registration and refresh silently free state. The use of the first nbtd interface socket assumes that primary interface routing is acceptable for all WINS client requests.

## Test Signals

Tests should cover successful registration, timeout retry, refresh success, refresh timeout re-registration, rejected rcode marking conflict, missing address list, multiple configured WINS servers, and refresh timer calculation with `nbtd:max_refresh_time` and TTL boundaries.
