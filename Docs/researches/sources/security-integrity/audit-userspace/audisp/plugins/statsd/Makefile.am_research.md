# sources/security-integrity/audit-userspace/audisp/plugins/statsd/Makefile.am

Purpose: builds and installs the `audisp-statsd` plugin and configs.

Important APIs and data: defines source `audisp-statsd.c`, plugin/program configs, man page, include paths, libaudit/auparse/aucommon/auplugin dependencies, and optional cap-ng linkage.

Control flow: automake install hook places plugin registration and program config with mode 0640.

State and persistence: no runtime state; controls installed plugin artifacts.

Dependencies and integration: integrates statsd plugin with audit userspace build and dispatcher configuration.

Risks: missing dependency updates can break plugin build or install. Config file mode/location must match runtime expectations.

Test signals: build/install checks and eventual plugin runtime tests.
