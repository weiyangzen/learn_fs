# File Research: sources/local-fs/ocfs2-tools/ocfs2_controld/dlmcontrol.c

`dlmcontrol.c` connects `ocfs2_controld` to `dlm_controld` through libdlmcontrol. It registers filesystem lockspaces before kernel mounts proceed, unregisters them on last unmount, and sends node-down notifications until dlm_controld acknowledges them.

It tracks registered filesystems in `register_list`, each with pending notification nodes and a registration result callback. The fd from `dlmc_fs_connect()` is added to the main poll loop, and result messages drive register completion or notification retry/cleanup.

Failure policy is conservative: unexpected errors in notification paths call `shutdown_daemon()` because OCFS2 cannot safely continue without ordered DLM coordination.
