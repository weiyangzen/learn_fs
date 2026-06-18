# sources/security-integrity/audit-userspace/audisp/plugins/remote/audisp-remote.conf

Purpose: default configuration for remote audit logging.

Important APIs and data: includes remote server/port, transport, queue file/depth, mode, format, retry/heartbeat parameters, failure actions, overflow action, startup action, and optional Kerberos principal/client/key file entries.

Control flow: parsed by `remote-config.c`; `audisp-remote.c` uses the values to select queue mode, transport, retry behavior, and response to errors.

State and persistence: installed under `/etc/audit`, root-owned mode 0640 by the Makefile; values persist across daemon restarts.

Dependencies and integration: must be valid before enabling `au-remote.conf`. `mode = forward` only works with `format = managed`.

Risks: `remote_server` is blank by default, so enabled deployments require administrator configuration. Actions like `stop`, `suspend`, `single`, and `halt` are operationally significant.

Test signals: config parser tests for every option, action keyword, invalid combinations, and GSS-disabled builds.
