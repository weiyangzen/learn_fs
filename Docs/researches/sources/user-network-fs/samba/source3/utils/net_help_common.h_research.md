# sources/user-network-fs/samba/source3/utils/net_help_common.h

Purpose: declares shared common-help functions for `net` command modules.

Important APIs/types/functions: declares `net_common_methods_usage()` and `net_common_flags_usage()`, both taking `struct net_context *`, `argc`, and `argv`.

Control flow: none; include guard `_NET_HELP_COMMON_H_` protects declarations.

State and persistence: none.

Dependencies/integration: used by modules that print common method/flag help. Header comments document purpose, parameters, and nominal return contract.

Risks: comments say nonzero on failure, while `net_common_flags_usage()` returns `-1` after normal output; callers need context-aware status handling.

Test signals: compile include users; declaration/implementation match; command help includes common text.
