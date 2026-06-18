# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/enum.py

Purpose: provides `EnumLocalAdmins`, a helper for enumerating local Administrators group membership over an existing SMB connection after relay.

Important APIs and control flow: the constructor stores the SMB connection and fixed named-pipe bindings for SAMR and LSARPC. `getLocalAdmins()` calls private `__getLocalAdminSids()` and `__resolveSids()`. `__getDceBinding()` builds a DCE/RPC transport and attaches the existing SMB connection. `__getLocalAdminSids()` binds SAMR, opens the Builtin domain, opens alias RID 544, and returns member SIDs. `__resolveSids()` binds LSAT/LSAD, opens policy, looks up SIDs, and formats `DOMAIN\Name` strings.

State and persistence: only stores the supplied SMB connection and binding strings. No persistent storage; network RPC calls are the side effect.

Dependencies and integration: depends on Impacket DCE/RPC transport, SAMR, LSAT, LSAD, and `MAXIMUM_ALLOWED`. It integrates with relay attack logic that wants local admin status.

Risks and test signals: private methods do not use `try/finally`, so exceptions can leave DCE connections open. Alias RID 544 assumes the standard Administrators alias. Tests should mock DCE transports to verify bind/open call order, returned SID formatting, name formatting, disconnect behavior on success, and exception behavior for access denied or unknown SIDs.
