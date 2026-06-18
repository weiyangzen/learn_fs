# File Research: sources/local-fs/ocfs2-tools/ocfs2_controld/cman.c

`cman.c` is the CMAN stack adapter for `ocfs2_controld`. It initializes normal and admin CMAN handles, gets the cluster name and local node id, tracks node membership snapshots, registers CMAN notification callbacks, and adds the CMAN fd to the daemon poll loop.

It implements the stack interface declared in `ocfs2_controld.h`: cluster validation, cluster name lookup, node id to name lookup, node kill via `cman_kill_node()`, setup, and teardown. Shutdown requests are denied while OCFS2 mounts exist.

Risk notes include membership tracking being mostly diagnostic, a FIXME about waiting for local membership, and daemon shutdown if the CMAN connection dies.
