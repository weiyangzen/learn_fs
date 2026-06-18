# sources/security-integrity/audit-userspace/audisp/plugins/ids/rules/25-connections.rules

Purpose: installs audit rules that tag execution of common network/data movement tools with `ids-connections`.

Important APIs and data: rule lines watch executable paths such as curl, ftp, git, rsync, scp, sftp, ssh, wget, telnet, nc/ncat, nmap/nping, and ping with `auid>=1000`, `auid!=-1`, `perm=x`, and key `ids-connections`.

Control flow: auditd evaluates rules on execution; matching events later reach `model_behavior.c`, which adds six points to the session for `ids-connections`.

State and persistence: rules are installed under the audit rules directory by the IDS rules Makefile; active audit kernel state persists until rules are reloaded.

Dependencies and integration: depends on executable paths existing at `/usr/bin/...` and on behavior model key matching.

Risks: path-specific rules miss alternate locations and may fail if tools are absent. Network tools are legitimate for many users, so scoring can create false positives.

Test signals: `auditctl` rule loading and execution of watched binaries should produce events with key `ids-connections`.
