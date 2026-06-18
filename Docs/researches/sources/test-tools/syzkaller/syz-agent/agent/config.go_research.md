# sources/test-tools/syzkaller/syz-agent/agent/config.go

Purpose: JSON configuration loader for syz-agent.

Important APIs/types/functions: `TargetConfig`, `Config`, and `loadConfig`.

Control flow: loads JSON with defaults for syzkaller repo/branch, cache size, Gemini key, and cloud project; splits target strings via `mgrconfig.SplitTarget`; resolves VM `gcs_path` through `gcpsecret`; resolves dashboard, model, and cloud secrets; and exports resolved Gemini/cloud project values to process environment.

State and persistence: mutates loaded config and process env vars `GOOGLE_API_KEY` and `GOOGLE_CLOUD_PROJECT`.

Dependencies and integration points: uses `pkg/config`, `pkg/gcpsecret`, and `pkg/mgrconfig`; consumed by `agent.go`.

Risks: secret resolution happens synchronously at startup. VM config is decoded as generic JSON, so malformed or non-object VM data fails. Environment mutation can affect libraries globally.

Test signals: `config_test.go` covers plain values and `env:` resolution for key fields.
