## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_link.c

Purpose: implements hard-link creation.

APIs and flow: `_9p_link` parses directory fid, target fid, and link name; validates both fids; initializes op context from the destination directory; enforces write access and same-export constraints; copies the link name; calls `fsal_link(target, dir, name)`; and returns `RLINK`.

State/dependencies: no fid mutation occurs, but filesystem namespace state changes through FSAL. It depends on export ids to reject cross-export links and on FSAL link semantics for permissions and link counts.

Risks/tests: test cross-export `EXDEV`, long names, read-only exports, invalid target/dfid, link to directories if FSAL forbids it, and post-link attribute/cache consistency.
