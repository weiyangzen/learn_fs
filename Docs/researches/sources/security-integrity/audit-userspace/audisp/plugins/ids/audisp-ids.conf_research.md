## sources/security-integrity/audit-userspace/audisp/plugins/ids/audisp-ids.conf

Purpose: audisp plugin config for the experimental IDS.

It is inactive by default, runs `/usr/sbin/audisp-ids`, type `always`, passes one argument, and receives string format. State is parsed by dispatcher pconfig. Risks include path mismatch with install prefix/sbin settings and inactive default hiding runtime issues. Test signal is enabling with `ids.conf` and sending audit events through auplugin.
