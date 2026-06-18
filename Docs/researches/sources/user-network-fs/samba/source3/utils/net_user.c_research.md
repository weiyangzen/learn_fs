# sources/user-network-fs/samba/source3/utils/net_user.c

## Purpose
Routes `net user` operations for list, add, delete, rename, and info across ADS, RPC, and RAP backends.

## Important APIs, Types, and Functions
`net_user_usage()` prints command syntax and common flags. `net_user()` handles no-argument usage, `HELP`, ADS selection via `net_ads_check()`, RPC-PDC selection via `net_rpc_check(c, NET_FLAGS_PDC)`, and RAP fallback.

## Control Flow
ADS is preferred when available. RPC against a PDC is the next choice. RAP handles the remaining case.

## State and Persistence
This file itself has no persistence. Selected backends may mutate directory, SAMR/passdb, or RAP-accessible user databases.

## Dependencies and Integration Points
Integrates the generic `net` command with ADS/RPC/RAP user backends and common usage helpers.

## Risks
Different backends have different semantics and option coverage. The RPC path may default to a PDC when the user did not specify a server.

## Test Signals
Cover no-arg usage, `HELP`, ADS dispatch, RPC fallback, RAP fallback, and argument preservation through dispatch.
