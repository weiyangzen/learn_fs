# sources/security-integrity/audit-userspace/init.d/auditd.conf

Purpose: Default audit daemon configuration controlling local logging, log rotation, disk-space actions, network listener defaults, plugin queueing, and event timeout behavior.

Important settings: Enables local events and logs, writes `/var/log/audit/audit.log`, uses `ENRICHED` format, async incremental flushing, 8 MB log rotation with 5 logs, root log group, disk thresholds/actions, `use_libwrap = yes`, TCP listener placeholders, `transport = TCP`, `distribute_network = no`, `q_depth = 2000`, `overflow_action = SYSLOG`, `plugin_dir = /etc/audit/plugins.d`, and `end_of_event_timeout = 2`.

Control flow: Declarative config consumed by auditd at startup/reconfigure. Values drive internal daemon behavior for logging, rotation, queue overflow, network listener, and plugin dispatch.

State and persistence: Persistent system policy under `/etc/audit/auditd.conf` when installed. Controls audit log files and daemon runtime behavior.

Dependencies and integration: Used by `auditd`, systemd service, plugin directory, libwrap support from configure/build, optional Kerberos key file, and log directory created by tmpfiles.

Risks: Defaults like `disk_full_action = SUSPEND` and `disk_error_action = SUSPEND` can stop logging under storage failure. Network listener options are mostly commented but must be secured if enabled. `use_libwrap = yes` is meaningful only when built with tcp_wrappers. Queue depth and overflow action shape event loss behavior.

Test signals: `auditd -f` config parse, `auditd -s` reconfigure, log rotation tests, disk threshold simulations, plugin queue load tests, and listener startup tests when TCP options are enabled.
