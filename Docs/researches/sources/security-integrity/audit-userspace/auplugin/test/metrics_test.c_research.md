<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/test/metrics_test.c -->
# sources/security-integrity/audit-userspace/auplugin/test/metrics_test.c

Purpose: smoke test for auplugin stats callback registration and reporting.

Important APIs and functions: registers `cb` with `auplugin_register_stats_callback`, then calls `auplugin_report_stats`, which should invoke the callback with current queue depth, max depth, and overflow flag.

Control flow and state: no plugin initialization or queue traffic is created here; it checks that reporting safely calls through the registered function and prints the metric tuple.

Dependencies and integration: includes `auplugin.h` and links against `libauplugin`. Queue metric functions are supplied by the dispatcher queue dependency.

Risks and test signals: shallow coverage; it may expose uninitialized queue metric behavior depending on queue implementation defaults. Output `depth=... max=... ovf=...` is the visible signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/test/metrics_test.c -->
