# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/apinums.h

LAN Manager Remote Administration Protocol API number definitions.

Key behavior:
- Defines numeric constants for Microsoft LAN Manager APIs, including share, session, connection, file, server, audit, error log, char device, message, service, access, group, user, workstation, use, print, profile, statistics, NetBIOS, account replication, and related APIs.
- Preserves dead/replaced table entries as comments to maintain official numbering.
- Defines `MAX_API` as `215`.

Dependencies:
- Header-only constants, likely consumed by CIFS RAP transaction code elsewhere in the directory.

Research notes:
- This file is protocol-number mapping, not executable logic.
