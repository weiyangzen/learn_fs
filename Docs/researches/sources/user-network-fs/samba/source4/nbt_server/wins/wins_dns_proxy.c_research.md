# sources/user-network-fs/samba/source4/nbt_server/wins/wins_dns_proxy.c

## Purpose

`wins_dns_proxy.c` implements the WINS server fallback path that answers selected NetBIOS name queries by resolving the requested name through the host resolver. It is used when a WINS lookup misses and `wins dns proxy` is enabled, allowing client or server NetBIOS names to be proxied to ordinary host-name resolution.

## Important APIs, Types, and Functions

The public entry point is `nbtd_wins_dns_proxy_query()`. It allocates `struct wins_dns_proxy_state`, steals the incoming `nbt_name_packet`, copies the source socket address, creates a `resolve_context`, adds the host resolution method, and starts `resolve_name_send()`. Completion is handled by `nbtd_wins_dns_proxy_handler()`, which calls `resolve_name_recv()` and replies with `nbtd_name_query_reply()` or `nbtd_negative_name_query_reply()`.

## Control Flow

The server builds async state under the name socket, carries the packet and source address into the resolver callback, and runs the request on the nbtd service event context. A successful resolver result is wrapped in a one-element string list and sent as a positive NetBIOS query reply with zero TTL and currently fixed `nb_flags`. Allocation, address-copy, context, resolver, or resolution failures all fall through to a negative name query reply.

## State and Persistence Behavior

This file does not persist state. The only state is the talloc-owned async request state and packet ownership transferred into it. The packet lifetime must last until either the resolver callback sends a reply or setup failure sends a negative reply synchronously.

## Dependencies and Integration Points

It integrates with `nbt_server`, `winsdb.h`, `winsserver.h`, Samba composite async contexts, `resolve_context`, `resolve_name_send/recv`, socket address helpers, and the service task event loop. It is called by `nbtd_winsserver_query()` after an LDB WINS miss for `NBT_NAME_CLIENT` and `NBT_NAME_SERVER` names.

## Risks and Edge Cases

The reply uses `nb_flags = 0` with a TODO, so node/group semantics from DNS are not represented. Only the host resolver method is added, which intentionally avoids recursive WINS behavior but makes behavior depend on local resolver configuration. A setup failure after stealing the packet into `s` still replies using the original `packet` pointer; the talloc hierarchy keeps the object alive, but this ownership pattern is worth care during future edits.

## Test Signals

Useful tests include WINS misses with DNS proxy disabled and enabled, successful host resolution, resolver timeout/failure, allocation-failure paths, and verifying that only client/server NetBIOS name types use DNS proxy. Packet lifetime can be stressed with async resolver delays.
