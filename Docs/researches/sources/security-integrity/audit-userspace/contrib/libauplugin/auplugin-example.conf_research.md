# sources/security-integrity/audit-userspace/contrib/libauplugin/auplugin-example.conf

Purpose: Example audit plugin configuration for the `libauplugin` sample binary.

Important fields: `active = no`, `path = /sbin/auplugin-example`, `type = always`, `args = 1`, and `format = string`.

Control flow: No executable control flow; auditd/audisp reads this declarative file to decide whether to start the plugin, which binary to execute, and how to format events.

State and persistence: Persistent configuration under a plugin config directory when installed by an administrator. Default inactive state prevents accidental dispatch.

Dependencies and integration: Integrates with auditd plugin configuration semantics and the sample binary from `contrib/libauplugin`.

Risks: The path is hard-coded to `/sbin/auplugin-example`, which may not match distro layout. Enabling it without installing the binary or validating queue behavior can create auditd plugin errors.

Test signals: Place under an audit plugin directory, set `active = yes`, restart/reconfigure auditd, and confirm auditd starts the example and passes string-formatted events.
