# sources/test-tools/syzkaller/syz-agent/lore-relay/config.go

Purpose: YAML config loader for syz-lore-relay.

Important APIs/types/functions: `Config`, `SMTPConfig`, `loadConfig`, and `Config.ParseFrom`.

Control flow: reads YAML, applies default dashboard/lore poll intervals, resolves dashboard key and SMTP host/user/port/password via `gcpsecret`, and parses SMTP From with `net/mail`.

State and persistence: no file writes; config object holds resolved secrets in memory.

Dependencies and integration points: consumed by `main.go`; integrates with `pkg/gcpsecret` and `gopkg.in/yaml.v3`.

Risks: SMTP From is validated later, not during `loadConfig`. Secret resolution failures abort startup.

Test signals: no direct tests in this subset.
