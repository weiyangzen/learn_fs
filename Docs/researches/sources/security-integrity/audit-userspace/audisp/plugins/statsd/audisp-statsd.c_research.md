# sources/security-integrity/audit-userspace/audisp/plugins/statsd/audisp-statsd.c

Purpose: collects audit daemon/kernel status plus event counters and emits statsd metrics over UDP.

Important APIs and data: local config holds address, port, interval, socket, and resolved sockaddr. Report struct tracks kernel backlog/lost, auditd state report gauges, memory stats, and event counters. Key functions include `load_config`, `make_socket`, `get_kernel_status`, `get_auditd_status`, `send_statsd`, `statsd_timer`, `main`, and `handle_event`.

Control flow: main requires root, loads config, opens UDP socket, drops to CAP_AUDIT_CONTROL when available, opens audit netlink, initializes auplugin queue, and feeds events with a periodic timer. The timer gathers kernel and auditd state, sends one UDP statsd packet, and clears counters. Event handler increments counters by auparse-normalized result and first record type.

State and persistence: all counters are in memory and reset after each interval. Reads auditd state from `AUDIT_RUN_DIR/auditd.state`; emits no local persistent state.

Dependencies and integration: depends on libaudit status requests, auparse normalization, auplugin event feed, common time parser, and a statsd UDP endpoint.

Risks: config parser is simple first-character dispatch and requires all options. UDP send is best effort. Stats packet is capped at 512 bytes; additions risk truncation. Auditd state parsing depends on exact text labels.

Test signals: simulate config parsing, event types, timer flush, kernel status failures, and state-report parsing. No direct tests are present here.
