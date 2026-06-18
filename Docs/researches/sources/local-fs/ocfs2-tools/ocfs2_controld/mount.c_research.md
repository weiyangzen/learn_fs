# File Research: sources/local-fs/ocfs2-tools/ocfs2_controld/mount.c

`mount.c` manages OCFS2 filesystem mountgroups inside `ocfs2_controld`. A mountgroup is keyed by UUID, stores the source device, active services/mountpoints, CPG group pointer, DLM registration state, in-progress service, client fd/ci, and pending error state.

First mount creates a mountgroup, validates device identity, joins a CPG group, registers with dlm_controld, then notifies the mount client. Additional real mounts return `EALREADY` so the client can call `mount(2)` without repeating group setup. Last unmount unregisters DLM, leaves CPG, notifies the client, and frees the mountgroup.

Node-down callbacks tell the kernel control device and dlm_controld about departed nodes. Unexpected group leave while live causes an immediate `_exit(1)` after logging to encourage fencing/cluster recovery.

Risk areas include delicate in-progress state transitions, special handling when a mounter dies after notification but before known mount success, fail-fast unexpected leave behavior, and string/device validation relying on stat `st_rdev` comparisons.
