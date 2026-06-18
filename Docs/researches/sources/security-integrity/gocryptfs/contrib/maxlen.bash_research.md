# sources/security-integrity/gocryptfs/contrib/maxlen.bash

Purpose: This script probes maximum filename or path lengths through gocryptfs and backing filesystems.

Important APIs and steps: It creates progressively longer names, observes success/failure, and reports limits, often relevant to encrypted name expansion and long-name hashing.

Control flow and state: It mutates a temporary directory by creating/removing files with candidate names. Persistent state should be cleaned up after probing.

Dependencies and integration points: Supports validation of `-longnames`, `-longnamemax`, encrypted filename encoding, and filesystem limits.

Risks and test signals: Must avoid leaving extreme-name files behind. Signals are detected length boundaries and expected behavior on mounted encrypted filesystems.
