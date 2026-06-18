## sources/security-integrity/audit-userspace/audisp/audispd-config.h

Purpose: dispatcher daemon configuration structure.

`daemon_conf_t` stores queue depth, overflow action, max plugin restarts, and plugin directory. It extends auditd config types by including `auditd-config.h`. State is copied and owned by dispatcher runtime in `audispd.c`. Risks include string ownership around `plugin_dir` during reload and queue-depth changes requiring live queue resizing. Tests should cover dispatcher init/reconfigure with changed q_depth and plugin_dir.
