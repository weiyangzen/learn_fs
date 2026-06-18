# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/pcnfsd.c

This file implements a minimal PC-NFS daemon RPC service.

Key content:
- Registers program `150001`, versions 1 and 2, on port 1111.
- Version 2 procedures: null, info, and auth.
- Version 1 procedure: null and auth.

Key routines:
- `main` starts the shared RPC server.
- `pcinit` parses config, initializes facility status table, and reads UID maps.
- `pcinfo` returns version string, comment, and facility list.
- `scramble` decodes PC-NFS obfuscated strings using XOR `0x5b`.
- `pc1auth` and `pcauth` parse credentials, decode username/password fields, map the user through `pair2idmap("pcnfsd", host)`, and return uid/gid metadata.
- `pcnull` handles no-op requests.

Important interactions:
- Uses shared `server`, `argopt`, `readunixidmaps`, `pair2idmap`, `name2id`, `chat`, and RPC packing macros.
- Shares UID mapping infrastructure with the NFS bridge.

Research notes:
- Password contents are decoded and logged for debugging but not actually verified here.
- Unknown users fall back to uid/gid 1.
- Version 2 auth replies include a static home path `merrimack:/` and comment `Trust me.`.
