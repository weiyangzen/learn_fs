# sources/test-tools/syzkaller/syz-agent/agent/config_test.go

Purpose: unit tests for syz-agent config secret resolution.

Important APIs/types/functions: `TestConfigPlainValues` and `TestConfigEnvResolution`.

Control flow: each test writes a temporary config JSON, calls `loadConfig`, and asserts resolved dashboard client/key and Gemini key values.

State and persistence: temporary directory/files only; env-resolution test sets process environment variables.

Dependencies and integration points: verifies `gcpsecret.Resolve` behavior for literal and `env:` forms as used by `loadConfig`.

Risks: tests do not cover target splitting failures, VM `gcs_path`, cloud project env mutation, or missing targets.

Test signals: focused positive coverage for common local/prod secret formats.
