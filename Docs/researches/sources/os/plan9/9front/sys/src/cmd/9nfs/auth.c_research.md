# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/auth.c

This file contains disabled/stubbed NFS authentication pseudo-file hooks.

Key routines:
- `xfauth` returns nil.
- `xfauthread` logs and returns zero bytes.
- `xfauthwrite` logs and returns zero.
- `xfauthremove` logs and returns failure.

Important interactions:
- Called from NFS lookup/create/read/write/setattr paths when handling root-level `#user` authentication pseudo-files.
- Current behavior effectively disables this older authentication mechanism.

Research notes:
- The file comment states NFS authentication support is now disabled.
- Real host-owner authentication is handled separately in `authhostowner.c`.
