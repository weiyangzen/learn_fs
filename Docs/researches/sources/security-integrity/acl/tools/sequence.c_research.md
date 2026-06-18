## sources/security-integrity/acl/tools/sequence.c

Purpose: minimal linked-list implementation for ACL edit commands.

`cmd_init`/`cmd_free` allocate command records, `seq_init`/`seq_free` own list lifetime, `seq_append` and `seq_append_cmd` add operations, `seq_get_cmd` iterates with `SEQ_FIRST_CMD`/`SEQ_NEXT_CMD`, and `seq_delete_cmd` removes a command. Control flow is simple append-only except cleanup and deletion of set-operation preambles in `setfacl.c`. State is heap-backed `struct seq_obj` plus heap-backed `struct cmd_obj` nodes. Dependencies are only libc allocation and `sequence.h`. Risks include no null-guard in `seq_free`, stale `s_last` when deleting the first and only entry, and caller reliance on list internals (`seq->s_last`) elsewhere. Tests should validate append/delete/iteration and empty-list behavior.
