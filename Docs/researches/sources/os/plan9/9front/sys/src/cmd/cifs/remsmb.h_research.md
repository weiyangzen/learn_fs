# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/remsmb.h

Microsoft-origin header defining descriptor strings for SMB transaction remote API calls. It is guarded by `_REMDEF_` and primarily consists of `#define` constants.

Descriptors cover share, session, connection, file, server, group, user, workstation, use, print queue/job/destination, profile, statistics, time-of-day, NetBIOS, config, domain controller, account sync/update, path/name, RPL, and miscellaneous LANMAN API layouts.

The CIFS implementation uses selected descriptors from this header in `trans.c`, especially for share enumeration/info, sessions, users/groups, server enumeration, and open file enumeration.

This file is protocol metadata rather than executable logic. The comments explain descriptor naming conventions and the remote API assumption that return parameter length must not exceed send parameter length.

Research relevance: it shows the CIFS client depends on old RAP/LANMAN descriptor-string encoding for administrative queries, not only file-oriented SMB operations.
