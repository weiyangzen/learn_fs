# sources/test-tools/syzkaller/syz-agent/lore-relay/main.go

Purpose: executable entry point for relaying dashboard/lore patch email workflows.

Important APIs/types/functions: `main` with flags `-config` and `-test-email`.

Control flow: loads config, creates dashboard client, creates lore poller using `/lore-repo/checkout`, creates SMTP sender, optionally sends a test email and exits, then constructs `lorerelay.NewRelay`, handles interrupts through context cancellation, and runs the relay loop.

State and persistence: lore checkout state persists under `/lore-repo/checkout`; relay sends email and updates dashboard through external services.

Dependencies and integration points: integrates dashboard API, lore poller, email sender, debug tracing, and `pkg/lore-relay`.

Risks: SMTP credentials or lore repo state failures stop the service. Test email path can send real mail from production config.

Test signals: no unit tests here; operational logs and `-test-email` are primary signals.
