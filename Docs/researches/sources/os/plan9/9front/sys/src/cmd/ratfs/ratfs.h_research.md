# File Research: sources/os/plan9/9front/sys/src/cmd/ratfs/ratfs.h

This is the shared header for ratfs.

Key definitions:
- QID constants for root, action directories, trusted files, generated address files, ctl, and dummy nodes.
- Node type constants: static directories, address directories, IP/account address holders, trusted directory/files, ctl file, and dummy node.
- Core structures:
  - `Fid` for active 9P fids,
  - `Cidraddr` for IP/mask pairs,
  - `Address` for account or CIDR entries,
  - `Node` for filesystem tree nodes,
  - `Keyword` for command/action parsing.
- Global state: `root`, `dummy`, `srvfd`, protocol buffer, debug fd, file paths, reload timestamps, and `trustedqid`.

Declared APIs:
- Tree and protocol functions: `io`, `newnode`, `walk`, `dread`, `hread`.
- Config/control functions: `getconf`, `reload`, `cidrparse`, `findkey`, `subslash`.
- Utilities: `atom`, `fatal`, debug printers, `cleantrusted`, `finddir`.

Implementation notes:
- `Node` uses a union for children, address arrays, or CIDR data depending on type.
- Several semantics depend on atomized strings for cheap equality.
