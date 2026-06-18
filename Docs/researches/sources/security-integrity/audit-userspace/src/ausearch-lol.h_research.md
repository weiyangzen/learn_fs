## sources/security-integrity/audit-userspace/src/ausearch-lol.h

Purpose: public interface for event assembly from raw audit records.

Important APIs/types: `lol_t` states `L_EMPTY`, `L_BUILDING`, and `L_COMPLETE`; `lolnode` stores an `llist *` and status; `lol` stores the dynamic node array, highest used index, and capacity. Public functions create, clear, add records, terminate/complete pending events, fetch ready events, and set EOE timeout.

Control flow/state: callers repeatedly call `lol_add_record()` and then `get_ready_event()`; returned lists must be cleared/freed by the caller.

Dependencies/integration: includes `ausearch-llist.h`; integrated into `ausearch.c`, `aureport.c`, and `ausearch-report.c` for timeout retrieval.

Risks/test signals: the header exposes array internals, so misuse can corrupt assembler state. Tests should validate ownership transfer and that `lol_clear()` does not double-free returned events.
