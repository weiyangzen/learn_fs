# sources/sync-backup/casync/test-files/test-files.sh

Purpose: creates the fixture tree used by casync integration tests.

Important APIs/types/functions: shell commands create regular files, sparse or random content, directories, links, device-like entries when permitted, and metadata combinations expected by archive/digest tests.

Control flow/state: mutates the current working directory by laying out deterministic test files. It is meant to be run from test setup, not sourced as a library.

Dependencies/integration: consumed by `test-script.sh.in`, FUSE/NBD variants, and source-tree fixture copying. It depends on standard Unix tools and root privileges for any privileged node/metadata cases.

Risks/test signals: environment-sensitive fixtures can differ when run unprivileged or on filesystems lacking special metadata support. The integration scripts compare list/mtree/digest output against this tree.

Source research group: `subset-b-009122`.
