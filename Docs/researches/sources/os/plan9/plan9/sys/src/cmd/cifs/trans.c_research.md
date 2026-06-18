# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/trans.c

Implements SMB_COM_TRANSACTION wrappers for RAP/LANMAN calls through `\\PIPE\\LANMAN`. Local helpers build transaction headers, fill parameter/data offsets and counts, dispatch via `cifsrpc`, and position packet cursors on returned parameter/data blocks.

Exposes RAP helpers for share enumeration/info, sessions, groups and group users, users and user info, server/domain/workstation enumeration, and open-file enumeration. It uses `apinums.h`, `remsmb.h`, `raperrstr`, and `pack.c` offset-string conversion.

The code handles partial/more-info responses imperfectly but includes resume loops for `NetUserEnum2`, `NetServerEnum3`, and `NetFileEnum2`.
