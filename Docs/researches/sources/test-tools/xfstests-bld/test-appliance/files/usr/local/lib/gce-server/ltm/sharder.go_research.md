# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/sharder.go

Purpose: schedules a full LTM test request across multiple shards, aggregates shard outputs, emails results, reports back to KCS for bisect flows, and uploads aggregate artifacts.

Important type/API: `ShardScheduler` stores request/test metadata, GCE config, kernel info, shard controls, result state, log/aggregate paths, parsed args/configs, GCP service, and shard list. Important methods include `NewShardScheduler`, `initLocalSharding`, `initRegionSharding`, `getKernelInfo`, `Run`, `finish`, `aggResults`, `concatResults`, `createInfo`, `createRunStats`, `genResultsSummary`, `emailReport`, `sendKCSReport`, `sendWatcherResult`, `packResults`, `clean`, and `SharderStatus`.

Control flow: decode original command, load GCE config, parse shardable configs via `parser.Cmd`, query kernel info with `gce-xfstests get-kernel-info`, open GCP service, choose region or local sharding from quotas, start all shards concurrently, aggregate result directories/serial logs, concatenate common files, generate summary/JUnit with `gen_results_summary`, determine pass/fail/error, email reports, tar/xz/upload aggregate results and XML, optionally upload summary, notify KCS or watchers, then clean local aggregate state.

State and dependencies: global `sharderMap`, local logs under `/var/log/go/ltm_logs`, aggregate directory, GCS uploads/deletes, Compute quotas, zone avoid list, and in-process shard status. Depends on `util/gcp`, `util/parser`, `util/server`, `gce-xfstests`, `gen_results_summary`, `tar`, `xz`, and SendGrid.

Risks and test signals: `getConfigs` returns nil error on parser error, which may hide invalid commands. `initLocalSharding` uses `mymath.MaxInt` for maxShards override, which increases rather than caps. Region sharding assumes zone quota availability maps to shard capacity. Tests should cover config splitting, quota-driven shard counts, summary classification, aggregate uploads, and KCS watcher callbacks.
