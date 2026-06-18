# sources/security-integrity/audit-userspace/audisp/plugins/ids/rules/25-unpacking.rules

Purpose: tags archive pack/unpack utilities as potential staging behavior.

Important APIs and data: watches unzip, tar, bunzip, zipgrep, gzip, gunzip, zcat, zgrep, and zless with `perm=x`, user auid filters, and key `ids-archive`.

Control flow: behavior model maps `ids-archive` to a five-point session score increase.

State and persistence: persistent only as installed audit rules.

Dependencies and integration: keyed to behavior model string matching and specific `/usr/bin` paths.

Risks: normal file handling can trigger the same key, so thresholds must account for expected user activity.

Test signals: execution of watched archive tools should create `ids-archive` events that are visible to audisp-ids.
