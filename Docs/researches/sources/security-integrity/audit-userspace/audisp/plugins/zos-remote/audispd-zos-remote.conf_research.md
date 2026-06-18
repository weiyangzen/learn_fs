# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/audispd-zos-remote.conf

Purpose: dispatcher registration for the z/OS remote audit plugin.

Important APIs and data: disabled by default, path `/sbin/audispd-zos-remote`, type `always`, args `/etc/audit/zos-remote.conf`, and string format.

Control flow: dispatcher launches the plugin and passes the zOS-specific config path as an argument.

State and persistence: persistent plugin config under plugins.d.

Dependencies and integration: depends on installed `zos-remote.conf` and the zOS plugin binary.

Risks: enabling without valid LDAP/RACF config will fail startup or event submission.

Test signals: dispatcher config parse and startup with missing/valid args.
