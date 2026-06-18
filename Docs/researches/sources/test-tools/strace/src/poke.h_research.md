<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/poke.h -->
# sources/test-tools/strace/src/poke.h

Purpose: declares poke payload storage and application APIs for syscall tampering.

Important APIs/types/functions: `struct poke_payload`, `alloc_poke_data`, `poke_add`, and `poke_tcb`.

Control flow: no implementation flow; callers create payloads, register them under an index, and apply by phase.

State and persistence behavior: `struct poke_payload` embeds list linkage and owns a data pointer supplied by callers.

Dependencies and integration points: included by injection parser and `poke.c`; requires `struct list_item` from surrounding includes.

Risks: ownership of `data` is external to the header and must be consistent with parser cleanup. `data_len` is 16-bit though comments document a maximum of 1024.

Test signals: compile-time users, parser-created payloads, and entry/exit application through `poke_tcb`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/poke.h -->
