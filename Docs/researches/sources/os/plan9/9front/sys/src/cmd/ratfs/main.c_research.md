# File Research: sources/os/plan9/9front/sys/src/cmd/ratfs/main.c

This file is the entry point and tree initializer for `ratfs`, a 9P filesystem exposing mail ratification/blocking policy.

Key responsibilities:
- Defines default paths:
  - service file `/srv/ratify`,
  - mountpoint `/mail/ratify`,
  - control file `/mail/lib/blocked`,
  - config file `/mail/lib/smtpd.conf.ext`.
- Defines the prototype filesystem tree: root, allow/delay/block/dial/deny directories, trusted directory, ctl file, and generated `ip`/`account` subdirectories.
- `main()` parses options, initializes formatters, builds the root tree, loads config/control files, posts a service pipe, forks the protocol server, and mounts it.
- `setroot()` materializes the static tree and initializes the reusable dummy node for generated address pseudo-files.
- `post()` publishes the service in `/srv/ratify`, replacing stale entries and exiting if another server is already mountable.
- `fatal()` prints an error and exits.
- `newnode()` allocates and links `Node` records.
- Debug helpers print nodes, fids, and full trees.

Options:
- `-c` alternate config file.
- `-f` alternate control file.
- `-m` alternate mountpoint.
- `-d` debug to stderr.

Implementation notes:
- Most nodes are owned by atomized `"upas"` strings.
- The server child seals stdin/stdout to `/dev/null` and runs `io()` from `proto.c`.
