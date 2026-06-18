## sources/security-integrity/audit-userspace/audisp/plugins/filter/filter.conf

Purpose: audisp plugin config for the filter plugin.

It is inactive by default, runs `/sbin/audisp-filter`, passes `allowlist /etc/audit/audisp-filter.conf /sbin/audisp-syslog LOG_USER LOG_INFO interpret`, and expects string input. State is parsed by dispatcher pconfig and determines child plugin chain. Risks include inactive default, hard-coded downstream syslog path, and allowlist mode with empty rules forwarding all events. Test signal is enabling the plugin with a rule file and confirming downstream output.
