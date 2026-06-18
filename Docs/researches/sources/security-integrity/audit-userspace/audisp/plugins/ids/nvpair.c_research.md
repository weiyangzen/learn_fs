# sources/security-integrity/audit-userspace/audisp/plugins/ids/nvpair.c

Purpose: provides a minimal singly linked list for delayed timer jobs with an argument string and expiration time.

Important APIs and data: implements `nvpair_list_create`, `nvpair_list_append`, `nvpair_list_find_job`, `nvpair_list_delete_cur`, and `nvpair_list_clear` over `nvlist`/`nvnode`.

Control flow: append copies job metadata and takes ownership of the `arg` pointer from the source node. `find_job` scans from the head for the first expired entry and positions `cur`/`prev`; delete frees the current node and its `arg`; clear frees all nodes.

State and persistence: list state is caller-owned memory. It is used by timer services and is not persisted.

Dependencies and integration: depends on `timer-services.h` for `jobs_t`. `timer-services.c` relies on `find_job` positioning the current item before deletion.

Risks: `nvpair_list_append` assumes `l->cur` is meaningful when appending to a non-empty list; callers must not corrupt cursor state. `delete_cur` does not advance `cur` after deletion, so callers should search again before using it.

Test signals: append/find/delete/clear with head, middle, tail, and empty-list cases; timer services exercise the expired-job path.
