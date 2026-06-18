# File Research: sources/local-fs/ocfs2-tools/ocfs2_controld/cpg.c

`cpg.c` manages Corosync/OpenAIS CPG groups for the daemon and per-filesystem mount groups. It maintains `cgroup` objects with CPG handles, poll-loop clients, current members, locally tracked nodes, callbacks, and user data hooks for mount code.

The daemon joins `ocfs2:controld`; each mounted filesystem joins `ocfs2:<uuid>`. Configuration change callbacks are copied into group state, then processed in the main loop. Daemon-group leaves trigger node-down handling for all mount groups; filesystem-group joins/leaves call mount-layer callbacks.

The code deliberately fences/kicks nodes whose `ocfs2_controld` process goes down while the node remains up. Risks include strict dependence on correct CPG ordering, fail-fast daemon shutdown when membership bookkeeping is inconsistent, and several comments marking incomplete behavior around daemon-group node leave processing.
