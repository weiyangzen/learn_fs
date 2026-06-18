# sources/test-tools/syzkaller/pkg/stat/set.go

## Purpose

`set.go` implements syzkaller's in-process metric registry, values, collection UI rows, graph history, rate formatting, distribution histories, and optional Prometheus gauge export.

## Important APIs, Types, And Functions

Global helpers `New`, `Collect`, and `RenderGraphs` delegate to a global ticking registry. `set.New` creates `Val` metrics with options: `Level`, `Link`, `Prometheus`, `Rate`, `Distribution`, `Graph`, `StackedGraph`, `NoGraph`, external `func() int`, and custom formatter. `Val.Add` and `Val.Val` update/read counters, external values, or histogram means. `Collect` returns sorted UI rows; `RenderGraphs` returns `UIGraph`/`UIPoint` history. `LenOf` builds external length metrics, and `FormatMB` formats byte counters.

## Control Flow

`newSet` optionally starts a one-second ticker. Each `tick` creates graph lines lazily, records max counter values, rate deltas, or per-period histograms, and advances history positions after `historyScale` ticks. When full, `compress` halves history resolution and doubles the scale, preserving maxes for counters, averages for rates, and one available histogram for distributions. `RenderGraphs` orders lines by creation order and expands distribution lines into 10/50/90 percentiles.

## State, Dependencies, Integration, And Risks

State is protected by `set.mu`, while metric counters use atomics and histogram samples use `histMu`. Dependencies include Prometheus client, `gohistogram`, `sync/atomic`, reflection, and sorting helpers. Integration points are manager/fuzzer UI, heartbeat logs, Prometheus scraping, and RPC server stats. Risks include duplicate metric names overwriting registry entries, ignored Prometheus registration errors, unsigned atomic underflow when `Add` receives negatives, graph stacked flag being graph-wide and last-writer sensitive, and long-running compression losing detail. Tests stress concurrency and history behavior.
