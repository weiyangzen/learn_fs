## sources/security-integrity/audit-userspace/src/ausearch-lol.c

Purpose: “list of lists” assembler that groups audit log lines into complete events and returns ready `llist` instances in chronological order.

Important APIs/functions: `lol_create()`, `lol_clear()`, `lol_add_record()`, `terminate_all_events()`, `complete_all_events()`, `get_ready_event()`, `lol_set_eoe_timeout()`, and `lol_get_eoe_timeout()`. Internal helpers parse timestamps (`extract_timestamp()`, `str2event()`), compare identities, grow the array, and mark events complete.

Control flow: each input line is timestamp-filtered, copied into an `lnode`, split into raw/enriched portions, and appended to an existing building event or a new `llist`. Events become complete when an end-of-event timeout has elapsed or a known last-record type is seen. `get_ready_event()` returns the complete event with lowest timestamp and transfers ownership to the caller.

State/persistence: process-local static `ready`, global `very_first_event`, and static `eoe_timeout`; no persistence. The `lol` array dynamically grows in blocks of 80.

Dependencies/integration: used by both `ausearch.c` and `aureport.c`; depends on `libaudit` helpers, common time filters, auditd log format constants, and `llist`.

Risks/test signals: timestamp extraction skips out-of-range records before assembly; this can affect multi-record events at range boundaries. `ready` is file-static, so multiple `lol` instances would interfere. Tests should cover enriched separator handling, node-prefixed logs, standalone EOE, interleaved events, array growth, stdin timeout completion, and malformed/fuzzer lines.
