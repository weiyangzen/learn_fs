# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/trans.c

Implements SMB `SMB_COM_TRANSACTION` wrappers for RAP/LANMAN remote administration calls over `\PIPE\LANMAN`.

Internal helpers build transaction headers (`thdr`), fill parameter/data offsets/counts (`ptparam`, `ptdata`), dispatch through `cifsrpc` (`trpc`), and move packet cursors to returned parameter/data sections.

Public RAP functions enumerate and query shares, sessions, groups, group users, users, user info, servers/domains/workstations, and open remote files. They use API numbers from `apinums.h` and descriptor strings from `remsmb.h`.

Parsing relies on fixed-width RAP records plus converted string offsets via `gconv`. Multi-page APIs use returned resume keys or follow-up enumeration calls; several comments document Windows/Samba quirks and permission limitations.

Important consumers: `fs.c` info-file generators, `main.c` initial share enumeration, and open-file/session/domain/user/group synthetic views.

Risk notes: buffers are sized from server MTU and parsed manually; several functions trust `navail` for allocation and tolerate servers lying about entry counts by stopping at packet end.
