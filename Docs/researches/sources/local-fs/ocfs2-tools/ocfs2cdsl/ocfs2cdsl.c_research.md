# File Research: sources/local-fs/ocfs2-tools/ocfs2cdsl/ocfs2cdsl.c

`ocfs2cdsl.c` creates OCFS2 context-dependent symbolic links. It validates the target is on an OCFS2 mount, determines the filesystem root, builds `.cluster/common/<type>` and `.cluster/<type>/<value>` storage paths, moves or copies existing files/directories, and replaces the original with a symlink containing a context placeholder.

Supported context types include hostname, machine, OS, node number, machine+OS, uid, and gid, though the manpage documents fewer. Node number is read from `/proc/fs/ocfs2/<major>_<minor>/nodenum`. GLib handles path building, quoting, spawning shell commands, and file tests.

Options control copy/local behavior, no-common copy, force replacement, dry-run, verbosity, and quiet mode. Risks include executing shell commands (`cp -a`, `rm -rf`, `mkdir -p`) through quoted command strings, deprecated/legacy OCFS2 procfs dependence for nodenum, symlink-relative path complexity, and process exits deep inside helpers.
