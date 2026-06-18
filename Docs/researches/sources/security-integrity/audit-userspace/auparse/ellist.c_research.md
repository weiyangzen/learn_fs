# sources/security-integrity/audit-userspace/auparse/ellist.c

Purpose: Implements the event record linked list used by auparse to store all records belonging to one audit event and parse each raw record into name/value fields.

Important APIs, types, and functions: Public hidden functions include `aup_list_create()`, `aup_list_clear()`, `aup_list_next()`, `aup_list_append()`, `aup_list_set_event()`, `aup_list_goto_rec()`, and `aup_list_first_field()`. Internal helpers include `aup_list_last()`, `_audit_c2x()`, `escape()`, and `parse_up_record()`.

Control flow: `aup_list_append()` allocates an `rnode`, links it at the tail, initializes record metadata and `nvlist`, then calls `parse_up_record()`. Parsing separates raw record text from an optional interpretation suffix, duplicates the record into `nv.record`, tokenizes fields, handles `msg=audit` and `msg='...'` forms, trims punctuation, expands audit keys into virtual repeated `key` fields, parses SELinux AVC unlabeled fields, and records type, machine, syscall, syscall args, and CWD for later interpretation. `aup_list_set_event()` transfers host pointer ownership from an `au_event_t` into the list. `aup_list_clear()` frees all records, nvlists, raw record strings, event host, and stored CWD.

State and persistence: `event_list_t` stores head/current record pointers, count, event timestamp/serial/host, and event-level CWD. Each `rnode` owns raw record text and parsed nvlist state. No persistence.

Dependencies and integration points: Depends on `libaudit.h`, `interpret.h`, `common.h`, `nvlist`, `rnode`, and audit tokenization helpers. `auparse.c` uses this module for event assembly and cursor traversal; `expression.c` evaluates search expressions over `rnode` and its nvlist.

Risks and edge cases: Record parsing is intentionally tolerant of malformed/fuzzer data but can skip records with no fields. Key expansion allocates duplicate names/values and must match `nvlist_clear()` ownership rules. Special AVC parsing uses a fixed 256-byte temporary context and fails if permission text is too long. `parse_up_record()` mutates `r->record` by splitting at the interpretation separator. CWD ownership moves from records to the event list and must not double-free.

Test signals: Direct auparse parser tests should validate field extraction, key splitting, AVC parsing, CWD/realpath behavior, and malformed records. This subset's z/OS plugin uses field traversal and interpreted values, making this module part of that integration path.
