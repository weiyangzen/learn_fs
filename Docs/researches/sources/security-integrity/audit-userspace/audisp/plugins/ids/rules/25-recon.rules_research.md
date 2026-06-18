# sources/security-integrity/audit-userspace/audisp/plugins/ids/rules/25-recon.rules

Purpose: tags execution of common reconnaissance and system-discovery utilities with `ids-recon`.

Important APIs and data: watches tools such as uname, rpm/yum/dnf, w/who/whoami, netstat/ss/route/ifconfig/ip, mount, lsof, df, dig/host, last/lastlog, getent, history, watch, and sestatus for user audit IDs.

Control flow: matching audit records are scored by `model_behavior.c` as low-weight reconnaissance signals.

State and persistence: audit rules become kernel audit policy after installation.

Dependencies and integration: depends on path-specific binary locations and the key string `ids-recon`.

Risks: reconnaissance tools are also normal admin tools, and some paths may be distribution-specific or missing. The commented `id` rule shows deliberate tuning to reduce noise.

Test signals: executing watched binaries as a non-daemon audited user should produce `ids-recon` keyed records and a two-point session score.
