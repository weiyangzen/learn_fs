# sources/user-network-fs/samba/source3/utils/net_conf_util.h

Purpose: declares utility functions shared by configuration command modules.

Important APIs/types/functions: exports `bool net_conf_param_valid(const char *service, const char *param, const char *valstr);`.

Control flow: none; include guard `__NET_CONF_UTIL_H__` protects the declaration.

State and persistence: none directly; declared validation protects registry configuration writes.

Dependencies/integration: consumers need `bool` and Samba config context through normal includes. Used by `net_conf.c` and intended for RPC config command code.

Risks: nullable behavior for `service` is not documented in the header, so callers must follow implementation assumptions.

Test signals: compile include users; declaration/implementation match; nullable service static-analysis checks.
