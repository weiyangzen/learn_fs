# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/imap.py

Purpose: implements the IMAP SOCKS plugin used by ntlmrelayx to let a local SOCKS client reuse an already-relayed IMAP session without reauthenticating to the real server. `PLUGIN_CLASS`, `IMAPSocksRelay.PLUGIN_NAME`, and `PLUGIN_SCHEME` are consumed by the socks plugin loader in `socksserver.py`; `getProtocolPort()` binds the plugin to port 143.

Important APIs and control flow: `skipAuthentication()` fakes the server greeting, expects `CAPABILITY`, mirrors upstream capabilities while removing GSSAPI/NTLM/login-disabled options, adds PLAIN/LOGIN, extracts the username from `AUTHENTICATE PLAIN` or `LOGIN`, finds `activeRelays[username]`, and attaches `session.sock` plus `session.file`. `tunnelConnection()` reads client commands and delegates to `processTunnelData()`, which forwards commands, tracks tags, handles continuations, blocks `LOGOUT`, supports `IDLE`/`DONE`, and streams IMAP `APPEND` literals.

State and persistence: state is in-memory only: `username`, `session`, `relaySocket`, `relaySocketFile`, `idleState`, `shouldClose`, and shared `activeRelays`. On client disconnect it may send `DONE` and `CLOSE`, then stores the next IMAP tag in `session.tagnum`.

Dependencies and integration: depends on `base64`, `impacket.LOG`, and `SocksRelay`; assumes protocol client sessions expose `capabilities`, `sock`, `file`, and `tagnum`.

Risks and test signals: Python 3 byte/string handling is fragile, APPEND parsing assumes a specific argument position, and shared relay state is unsynchronized. Tests should cover capability rewriting, PLAIN/LOGIN username normalization, in-use rejection, LOGOUT suppression, IDLE cleanup, CLOSE behavior, and literal APPEND streaming.
