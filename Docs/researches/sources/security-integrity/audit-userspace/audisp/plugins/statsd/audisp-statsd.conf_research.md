# sources/security-integrity/audit-userspace/audisp/plugins/statsd/audisp-statsd.conf

Purpose: configures the statsd destination and report interval.

Important APIs and data: default `address = localhost`, `port = 8125`, and `interval = 15s`; comments document accepted time suffixes.

Control flow: parsed by `audisp-statsd.c` and converted into UDP socket target plus timer interval.

State and persistence: persistent local config under `/etc/audit`.

Dependencies and integration: depends on `time_string_to_seconds` syntax for interval and DNS/address resolution for address.

Risks: parser requires all three settings and does not support quoting or inline comments after values.

Test signals: parser tests for valid suffixes, missing keys, unknown options, and invalid intervals.
