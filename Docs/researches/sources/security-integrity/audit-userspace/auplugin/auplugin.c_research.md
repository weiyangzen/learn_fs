<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/auplugin.c -->
# sources/security-integrity/audit-userspace/auplugin/auplugin.c

Purpose: main runtime library for auditd plugins, moving inbound audit dispatcher records through an internal queue to either string callbacks or auparse feed callbacks.

Important APIs and functions: `auplugin_init` configures fd, queue depth/flags, nonblocking mode, and queue storage; `auplugin_stop` sets the atomic stop flag; `auplugin_event_loop` starts a dequeue-to-string worker; `auplugin_event_feed` starts a dequeue-to-auparse worker with optional timer aging; stats functions expose queue depth/max/overflow. `common_inbound` reads framed records with `auplugin_fgets` and enqueues `event_t` objects.

Control flow and state: global single-instance state includes inbound fd, queue config, worker thread, timer callback, stats callback, and atomic stop/dispatcher hup flags. Inbound runs on the caller thread until stop/EOF/error; outbound worker owns queue destruction after draining/stopping.

Dependencies and integration: uses pthreads, signals, syslog, `common.h` atomics, `libdisp.h` event headers, hidden `queue.h`, auparse feed APIs, and `auplugin-fgets`.

Risks and test signals: concurrency and lifecycle are core risks: only one plugin instance is supported, outbound string loop detaches while feed loop joins, and queue destruction is worker-owned. Stats and fgets tests give partial coverage; full event-loop behavior needs integration tests with dispatcher-style input.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/auplugin.c -->
