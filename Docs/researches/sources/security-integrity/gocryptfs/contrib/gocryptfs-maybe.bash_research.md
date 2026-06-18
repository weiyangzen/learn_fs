# sources/security-integrity/gocryptfs/contrib/gocryptfs-maybe.bash

Purpose: This convenience wrapper conditionally mounts or uses gocryptfs depending on whether a target appears already mounted or available.

Important APIs and steps: It parses shell arguments, checks mount/path state, and invokes `gocryptfs` only when needed.

Control flow and state: The script branches on filesystem/mount status and may create a FUSE mount. Persistent state is the resulting mount if it runs gocryptfs.

Dependencies and integration points: Used manually in workflows where encrypted directories should be mounted on demand.

Risks and test signals: Mount detection must be reliable to avoid duplicate mounts or missed mounts. Signals are idempotent repeated invocation and correct pass-through of gocryptfs arguments.
