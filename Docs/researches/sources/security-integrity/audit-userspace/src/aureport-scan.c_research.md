## sources/security-integrity/audit-userspace/src/aureport-scan.c

Purpose: implements the event classification and accumulation path for `aureport`. `scan()` calls `extract_search_items()` on an assembled `llist`, filters by node, success, and config action, then `per_event_processing()` dispatches to summary or detailed reporting based on globals from `aureport-options.h`.

Important APIs/functions: `reset_counters()` initializes global `summary_data sd`; `destroy_counters()` releases its string and integer lists; `scan()` is the report-side match gate; `per_event_summary()` aggregates by report type; `per_event_detailed()` emits matching events through `print_per_event_item()`; `do_summary_total()` updates cross-report totals. Helper classifiers include `classify_success()`, `classify_conf()`, `aggregate_anom_item()`, `aggregate_resp_item()`, and `aggregate_crypto_item()`.

Control flow: `aureport.c` assembles a complete audit event, loads interpretations for single/SYSCALL events, then calls `scan()` and `per_event_processing()`. Summary mode adds unique users, files, hosts, terminals, keys, pids, syscall names, AVC objects, anomaly classes, crypto classes, virtualization, integrity, and MAC records into `sd`. Detailed mode checks the requested report class and calls the output layer for each matching event.

State/persistence: all state is in process memory, primarily `sd`; no file persistence. List members are owned by `sd` and released at shutdown. The function relies heavily on global filters such as `event_failed`, `event_conf_act`, `event_node_list`, `report_type`, and `report_detail`.

Dependencies/integration: depends on `ausearch-parse.c` for field extraction, `ausearch-llist.h` event structures, `ausearch-string.c`/`ausearch-int.c` containers, `ausearch-lookup.c` for uid/syscall names, `libaudit` message constants, and output functions declared elsewhere.

Risks: `destroy_counters()` calls `ilist_create()` instead of `ilist_clear()` for several lists (`mac_list`, `crypto_list`, `virt_list`, `integ_list`), which looks like a leak/reset bug. Many branches assume `l->head` and parsed sublists exist after `scan()`. Summary counts use `l->head->type` after `list_find_msg_range()` changes `cur`, so type attribution can be first-record-biased. Test signals should cover every `report_type`, success/config filters, node filters, list cleanup under repeated runs, and malformed events from fuzzed audit logs.
