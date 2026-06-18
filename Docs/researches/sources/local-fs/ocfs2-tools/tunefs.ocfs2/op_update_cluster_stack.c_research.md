# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_update_cluster_stack.c

## Role

Implements `--update-cluster-stack`, updating on-disk OCFS2 cluster stack information to match the currently running cluster.

## Run Flow

`update_cluster_stack_run()` only performs the update when invoked under `TUNEFS_FLAG_NOCLUSTER`, which is how the main driver routes operations after `tunefs_open()` reports invalid stack information. If the filesystem is already configured for the running cluster, it prints a no-op message.

`update_cluster()` prompts with a critical warning, starts progress, obtains the running cluster descriptor with `o2cb_running_cluster_desc()`, writes it to the filesystem with `ocfs2_set_cluster_desc()`, frees the descriptor, and stops progress.

## Metadata Touched

- On-disk cluster descriptor via `ocfs2_set_cluster_desc()`

## Open Flags

Declared as `TUNEFS_FLAG_RW | TUNEFS_FLAG_NOCLUSTER`.

## Safety Model

The prompt warns that no other node may be using the filesystem while its cluster configuration is modified. The metadata write is wrapped in signal blocking.

## Notable Risks

- This operation changes cluster identity/configuration metadata. Misuse can make the filesystem unsafe in a multi-node cluster.
