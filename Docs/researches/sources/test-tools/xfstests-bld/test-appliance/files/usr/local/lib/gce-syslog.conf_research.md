# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-syslog.conf

Purpose: rsyslog configuration fragment for copying system logs into the results volume.

Important behavior: the file contains a single rule/config line used by `gce-setup` when installing `/etc/rsyslog.d/gce-syslog.conf`, after which rsyslog is restarted and setup syslog is captured.

State and dependencies: affects rsyslog routing and `/results` log collection. It is consumed by `gce-setup`.

Risks and test signals: a malformed single-line rsyslog rule can break log capture or rsyslog restart. Validation should run `rsyslogd -N1` in an appliance build and confirm `/results/syslog` content during shutdown.
