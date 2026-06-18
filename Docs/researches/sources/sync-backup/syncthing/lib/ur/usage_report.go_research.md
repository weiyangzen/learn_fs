# sources/sync-backup/syncthing/lib/ur/usage_report.go

Purpose: builds, previews, sends, and schedules anonymous usage reports; also measures hashing performance.

Important APIs and control flow: `Service` stores config, model, connections service, no-upgrade flag, and a buffered force-run channel. `ReportData` and `ReportDataPreview` call `reportData`. `reportData` computes folder totals/maxima from model global sizes, runtime memory, process RSS, CPU count, SHA-256 scanner benchmark, physical memory, folder/device feature counts, discovery/relay settings, upgrade capability flags, and v3 options including NAT type, GUI stats, pull/copy-order maps, ownership/xattr flags, and rate-limit counts. It calls `model.UsageReportingStats`, then clears fields above the accepted version. `sendUsageReport` JSON POSTs to configured URL with optional insecure TLS. `Serve` subscribes to config, waits initial delay, sends daily when `URAccepted >= 2`, and reacts to forced runs when acceptance/URL/unique ID changes. `CpuBench` runs repeated `scanner.Blocks` over random data and returns best MiB/s.

State and persistence: no local persistence here; reads config/model state and sends remote reports. `StartTime` and `blocksResult` are package globals.

Dependencies and integration: wired in app startup with model and connections service. Depends on config, db counts, protocol/scanner, upgrade, contract, dialer, process stats, and TLS.

Risks: report generation can be CPU-expensive due to benchmark. `CommitConfiguration` only watches UR fields. POST response status is not checked. Tests for this file are absent in the subset; contract tests cover version clearing.
