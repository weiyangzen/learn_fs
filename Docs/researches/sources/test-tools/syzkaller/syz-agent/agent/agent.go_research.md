# sources/test-tools/syzkaller/syz-agent/agent/agent.go

Purpose: long-running AI job agent for syzkaller dashboard workflows, with optional MCP server mode.

Important APIs/types/functions: `main`, `run`, `reportBuildError`, `setupUpdater`, `Server`, `Server.poll`, `Server.executeJob`, `Server.modelOverQuota`, `Server.resetModelQuota`, and `initState`.

Control flow: loads config, reads target kernel configs, optionally serves pprof/http, sets up auto-updater unless `-syzkaller` is supplied, creates an aflow cache and dashboard client, then either serves MCP for one target or loops polling dashboard AI jobs. Jobs are filtered by configured workflows and model quota state, executed through `aflow.Flow.Execute`, streamed to dashboard trajectory logs, and reported via `AIJobDone` unless canceled or over quota.

State and persistence: persists cache under `workdir/cache`; updater maintains syzkaller/current unless bypassed. In-memory state tracks over-quota models until daily reset.

Dependencies and integration points: integrates with `dashboard/dashapi`, `pkg/aflow`, `pkg/updater`, `pkg/vcs`, `pkg/osutil`, and target config parsing.

Risks: quota errors intentionally leave dashboard jobs unreported for retry. MCP mode blocks forever and requires exactly one target. Kernel config files are read at startup, so missing mounted config fails the agent.

Test signals: config tests cover parsing/secrets; no direct polling/execution unit tests in this subset.
