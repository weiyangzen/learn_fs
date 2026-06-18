# File Research: sources/local-fs/ocfs2-tools/ocfs2cdsl/ocfs2cdsl.8.in

This manpage documents `ocfs2cdsl`, a utility for creating context-dependent symbolic links on OCFS2. It explains CDSL types such as hostname, machine, OS, and node number; copy, force, dry-run, quiet, verbose, and version options; and the use case of per-node views of a shared path.

The examples describe moving/copying common data into `.cluster/...` and replacing the original path with a symbolic link whose target contains a context token like `{hostname}`.
