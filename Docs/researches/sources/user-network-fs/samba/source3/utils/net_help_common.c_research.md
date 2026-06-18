# sources/user-network-fs/samba/source3/utils/net_help_common.c

Purpose: centralizes common help text for `net` transport methods, targets, common options, connection options, and credentials.

Important APIs/types/functions: `net_common_methods_usage()` prints ADS/RPC/RAP methods. `net_common_flags_usage()` prints target, debug/config/logging, name resolution/protocol/netbios/realm, and credential/Kerberos/client-protection options.

Control flow: both functions only emit translated text. Methods returns `0`; flags returns `-1`.

State and persistence: none.

Dependencies/integration: called by command-specific usage helpers and top-level help.

Risks: callers returning `net_common_flags_usage()` report a failure-like status after normal help output. Help text may drift from parser behavior, and auto-detection wording does not capture each command's fallback order.

Test signals: help output coverage; return-code expectations in callers; localization extraction; consistency with actual option parser.
