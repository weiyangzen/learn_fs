# sources/user-network-fs/samba/source4/nbt_server/wins/winswack.c

## Purpose

`winswack.c` implements secure WINS challenge and release-demand helpers. WINS registration conflict handling uses challenges to ask existing owners whether they still hold a name, and WREPL uses IRPC proxy wrappers so NBT server sockets on port 137 can receive replies from Windows servers that ignore the source port.

## Important APIs, Types, and Functions

Public functions are `wins_challenge_send()`, `wins_challenge_recv()`, `nbtd_proxy_wins_challenge()`, and `nbtd_proxy_wins_release_demand()`. Internal async helpers include `wins_challenge_handler()`, `wins_release_demand_send()`, `wins_release_demand_recv()`, `wins_release_demand_handler()`, `proxy_wins_challenge_handler()`, and `proxy_wins_release_demand_handler()`.

## Control Flow

`wins_challenge_send()` builds a composite context and sends an NBT name query to the first current-owner address using the interface chosen by `nbtd_find_request_iface()`. Timeout advances to the next address and retries until an owner replies or the address list is exhausted. `wins_challenge_recv()` returns the owner-reported address list on success. Release demand follows a similar address iteration model with NBT release packets and timeout/retry behavior tuned for one versus multiple addresses. IRPC handlers translate generated proxy request arrays into local IO structures, start the async operation, defer the IRPC reply, and send the result in the callback.

## State and Persistence Behavior

No persistent database state is changed directly. State is held in composite contexts, `wins_challenge_state`, `wins_release_demand_state`, and IRPC proxy state. Successful challenge outputs transfer address ownership to the caller via talloc.

## Dependencies and Integration Points

It depends on nbtd interface lookup, NBT name query/release client APIs, composite async helpers, loadparm NBT port, service task event context, generated IRPC structures, and messaging via `irpc_send_reply()`. `winsserver.c` uses the challenge path for WACK conflict decisions; WREPL code uses proxy calls.

## Risks and Edge Cases

The challenge path assumes at least one address; callers must ensure non-empty address arrays. Timeouts advance sequentially, so large address lists increase WACK latency. Some failures map to internal errors rather than trying alternate routing. IRPC wrappers contain TODOs around PIDL inline IPv4 arrays and manually steal address strings, making ownership sensitive.

## Test Signals

Tests should cover first-address success, timeout failover, all-address timeout, interface lookup failure, challenge reply address propagation, release-demand timeout profiles, IRPC deferred replies, zero/invalid address input, and WINS registration conflict behavior that consumes these results.
