# File Research: sources/local-fs/ocfs2-tools/ocfs2_controld/ckpt.c

`ckpt.c` wraps the OpenAIS checkpoint service for `ocfs2_controld`. It initializes/finalizes the CKPT service, opens global/node checkpoints, reads/writes bounded named sections, retries transient `SA_AIS_ERR_TRY_AGAIN`, and maps AIS errors to negative errno values plus log messages.

Checkpoint names are prefixed with `ocfs2:`. The global daemon checkpoint is `ocfs2:controld`; node checkpoints are `ocfs2:controld:<nodeid>`. Section size, count, and id lengths are fixed, with validation before store/get.

The daemon uses these checkpoints for cluster-wide protocol negotiation and per-node maximum protocol advertisement. Risks include indefinite retry loops for busy/existing checkpoints, small fixed section size limiting future protocol data, and a debug-only main under `DEBUG_EXE`.
