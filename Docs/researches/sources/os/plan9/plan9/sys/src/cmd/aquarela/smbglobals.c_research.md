# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbglobals.c

Defines default SMB server/client global configuration.

Key data:
- `smbglobals` defaults max receive, Unicode enabled, native OS, Aquarela version, mailslot and LANMAN pipe paths, sector/allocation sizes, space conversion flag, and logging settings.

Key function:
- `smbglobalsguess` fills server name, NetBIOS name, account name, primary domain, default remark, and log fd depending on server/client mode.

Interactions:
- Read by negotiation, session setup, browser, service, RAP, and logging code.

Notable details:
- Default server share namespace includes `/n/local` via `smbservice.c`.
