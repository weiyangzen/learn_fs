# File Research: sources/os/plan9/plan9/sys/src/cmd/ratfs/main.c

Entry point and static tree builder for `ratfs`, a synthetic filesystem exposing mail ratification/blocking policy.

Main responsibilities:
- Defines defaults: `/srv/ratify`, `/mail/ratify`, `/mail/lib/blocked`, `/mail/lib/smtpd.conf.ext`.
- Describes the prototype tree:
  `/`, `allow`, `delay`, `block`, `dial`, `deny`, `trusted`, `ctl`, plus `ip` and `account` subdirs under each address directory.
- `main()` parses flags, installs `%I` CIDR formatter, builds root, loads config/control data, posts the server pipe, forks the protocol loop, and mounts it.
- `setroot()` constructs the static `Node` hierarchy and initializes the reusable `dummy` node.
- `post()` creates/reuses `/srv/ratify`, exiting early if an existing server can be mounted.
- `newnode()` allocates and links nodes, initializes Plan 9 `Dir` metadata, qids, ownership, mode, parent/child/sibling links.
- Debug helpers print nodes, fids, and the whole tree.
- `ipconv()` formats `Cidraddr` values.

Risk/notes:
- `Node.d.type` is used as a ratfs-specific node kind, not just a Plan 9 directory type.
- Children are inserted at the head of sibling lists.
- `dummy` is reused for dynamic address match results.
