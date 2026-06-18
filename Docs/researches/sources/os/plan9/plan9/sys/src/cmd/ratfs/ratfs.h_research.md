# File Research: sources/os/plan9/plan9/sys/src/cmd/ratfs/ratfs.h

Shared definitions for the ratfs synthetic filesystem.

Defines:
- RPC size and qid ranges for fixed nodes, trusted files, and address pseudo-files.
- Node kind constants: `Directory`, `Addrdir`, `IPaddr`, `Acctaddr`, `Trusted`, `Trustedperm`, `Trustedtemp`, `Ctlfile`, `Dummynode`.
- `Fid`: active 9P fid state, current node, open flag, user, directory index.
- `Cidraddr`: IPv4 address and mask.
- `Address`: account string or CIDR address entry.
- `Node`: synthetic tree node with `Dir`, child/address/trusted union, sibling/parent links, qid base, and counts.
- `Keyword`: string-to-code mapping helper.

Declares all cross-file ratfs globals: `root`, `dummy`, `srvfd`, shared RPC buffer, debug/config paths, reload mtimes, and trusted qid counter.

Risk/notes:
- The `Node` union depends strictly on `d.type`.
- `Dir` string fields are expected to be atomized in most paths.
