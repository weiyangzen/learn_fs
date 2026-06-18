# File Research: sources/os/linux/linux/fs/nfsd/idmap.h

Read completely: 60 lines.

NFSD NFSv4 idmapping interface for translating users/groups between numeric kernel ids and protocol names.

Key responsibilities:
- Declares per-net idmap initialization and shutdown when `CONFIG_NFSD_V4` is enabled, with no-op inline stubs otherwise.
- Declares name-to-UID, name-to-GID, user encoding, and group encoding helpers used by NFSv4 XDR paths.

Dependencies:
- Includes sunrpc service request types and NFS idmap definitions.

Notable risks:
- Header contains legacy BSD-style license text and one stray `> *` character in the comment block, but the declarations are straightforward.
- Callers must handle returned NFS status values rather than raw errno for mapping failures.
