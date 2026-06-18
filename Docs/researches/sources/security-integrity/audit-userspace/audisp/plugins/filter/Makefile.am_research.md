## sources/security-integrity/audit-userspace/audisp/plugins/filter/Makefile.am

Purpose: build/install fragment for `audisp-filter`.

It builds a hardening-enabled PIE plugin, links common, auparse, auplugin, and optional cap-ng, installs the plugin config in plugins.d and rule config in audit sysconf, and ships a manpage. State is installed binary/config. Dependencies are auparse expression support and configured install paths. Risks include default config launching `/sbin/audisp-syslog` and requiring both plugin and rule configs to be present. Test signal is build plus `audisp-filter --check`.
