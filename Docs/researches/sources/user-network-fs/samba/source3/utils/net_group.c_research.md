# sources/user-network-fs/samba/source3/utils/net_group.c

Purpose: implements generic `net group` front-end help and backend selection.

Important APIs/types/functions: `net_group_usage()` prints syntax and common flags; `net_group()` dispatches to ADS or RAP group commands.

Control flow: no args print usage. `HELP` prints usage and returns success. Otherwise `net_ads_check(c) == 0` selects `net_ads_group()`, with fallback to `net_rap_group()`.

State and persistence: no direct state; delegated commands can create/delete/modify remote groups.

Dependencies/integration: depends on `net_ads_check()`, `net_ads_group()`, `net_rap_group()`, common help printers, and group-related `net_context` options.

Risks: auto-detection can select ADS based on CLDAP reachability. Usage mentions RPC operations even this fallback path is ADS/RAP-oriented.

Test signals: usage/help; ADS reachable/unreachable dispatch; group add/delete/list/member through selected backend; option text consistency.
