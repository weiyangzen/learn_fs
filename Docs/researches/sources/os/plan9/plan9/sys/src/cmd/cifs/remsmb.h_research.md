# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/remsmb.h

Microsoft-derived descriptor string definitions for LAN Manager remote API calls. Defines structure descriptors and parameter descriptors for share, session, file, server, group, user, workstation, print, service, audit, config, account, and related APIs.

Used by `trans.c` to tell RAP servers how parameters and returned structures are encoded. Data-only header with include guard `_REMDEF_`.
