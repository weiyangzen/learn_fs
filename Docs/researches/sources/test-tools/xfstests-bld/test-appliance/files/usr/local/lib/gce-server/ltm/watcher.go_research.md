# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/watcher.go

Purpose: watches a remote Git branch and triggers KCS build plus LTM test runs when HEAD changes.

Important type/API: `GitWatcher` stores watcher ID, command, bucket/report settings, original task request, test history, pack history, build counter, remote repo handle, done channel, and log/result paths. Functions include `NewGitWatcher`, `Run`, `watch`, `InitTest`, `tidyUp`, `Clean`, `Info`, `UpdateTest`, `StopWatcher`, `WatcherStatus`, and `UpdateWatcherTest`.

Control flow: create a watcher with a unique test ID, parse bucket config and original command, initialize `git.RemoteRepository`, seed `ExtraOptions` for KCS builds, and register in `watcherMap`. The watch loop initializes a first test, then every minute polls remote HEAD with exponential skip backoff after update errors; on changes it starts another build/test. Every seven days it calls currently minimal `tidyUp`. Test completion updates are routed by splitting LTM test IDs back to watcher base IDs.

State and dependencies: in-memory `watcherMap` protected by `watcherLock`, per-watcher history protected by `historyLock`, logs under LTM log dir, remote Git via `git ls-remote`, KCS forwarding, and email on watcher failures.

Risks and test signals: watchers are not durable across LTM restart. `Clean` closes `done` after removal; sending to `done` concurrently can race if lifecycle is mishandled. `tidyUp` is intentionally a placeholder. Tests should mock remote head changes, stop behavior, history length, and KCS forwarding fields.
