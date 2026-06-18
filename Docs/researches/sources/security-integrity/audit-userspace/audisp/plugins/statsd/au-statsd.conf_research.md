# sources/security-integrity/audit-userspace/audisp/plugins/statsd/au-statsd.conf

Purpose: dispatcher registration for the statsd audit metrics plugin.

Important APIs and data: disabled by default, path `/sbin/audisp-statsd`, type `always`, string format.

Control flow: audit dispatcher launches the plugin when active.

State and persistence: persistent admin config under plugins.d.

Dependencies and integration: requires `audisp-statsd.conf` for destination address, port, and interval.

Risks: disabled default prevents metrics until explicitly enabled; wrong path breaks plugin startup.

Test signals: dispatcher config parsing and activation.
