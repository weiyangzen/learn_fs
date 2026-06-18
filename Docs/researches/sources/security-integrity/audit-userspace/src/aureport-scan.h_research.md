## sources/security-integrity/audit-userspace/src/aureport-scan.h

Purpose: declares the report scanner contract used by `aureport.c` and report output code. It defines the global aggregation structure for summary report production.

Important APIs/types: `summary_data` owns many `slist` and `ilist` accumulators plus scalar counters for config changes, crypto, account changes, logins, auth, events, AVCs, MAC, failed syscalls, anomalies, responses, virtualization, and integrity. Public functions are `reset_counters()`, `destroy_counters()`, `scan()`, `per_event_processing()`, `print_title()`, `print_per_event_item()`, and `print_wrap_up()`. It exports `summary_data sd`.

Control flow: callers initialize `sd` once, feed each parsed event through `scan()` and `per_event_processing()`, then call output wrap-up after all logs are processed.

State/persistence: exposes a process-global mutable `sd`; no persistence. Ownership of strings stored in its lists is managed by the scanner/list modules.

Dependencies/integration: includes `ausearch-llist.h` for event lists and `ausearch-int.h`, which indirectly relies on string lists through the included llist header.

Risks/test signals: because `sd` is global, tests must reset/destroy it between cases. ABI-sensitive changes to `summary_data` affect report output modules. Tests should validate initialization, cleanup, and that all list fields remain consistent after empty and populated reports.
