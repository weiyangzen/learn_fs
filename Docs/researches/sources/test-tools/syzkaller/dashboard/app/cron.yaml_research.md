# sources/test-tools/syzkaller/dashboard/app/cron.yaml

Purpose: App Engine cron schedule for recurring dashboard maintenance, polling, cache warming, coverage aggregation, exports, reports, and subsystem updates.

Important entries: email polling runs every minute; full cache update hourly; dungeon preheat hourly; minute UI cache update every minute; asset deprecation every three hours; KCIDB polling and subsystem refresh every five minutes; subsystem reports every eight hours. Coverage aggregation runs quarter merges weekly on Sunday midnight and day/month merges daily midnight. Coverage garbage cleanup runs Saturday noon, intentionally away from aggregation. Reproducer DB export runs Saturday midnight. Monthly coverage emails run on the 15th, and coverage DB subsystem regeneration runs every Monday.

Control flow and integration: each URL maps to handlers registered in `main.go`, `batch_main.go`, and other dashboard files. Query parameters on `/cron/batch_coverage` determine which period types and how many newest periods are merged.

State and persistence behavior: cron itself stores no state, but it drives datastore/memcache updates, Batch job creation, KCIDB/export side effects, coverage DB writes/deletes, email sends, and asset reference deprecation.

Dependencies and integration points: depends on App Engine cron syntax and on handlers being registered during `installConfig`/HTTP initialization. Operational timing comments document coverage propagation assumptions and cleanup race avoidance.

Risks: schedules are dense for minute-level tasks, so handler idempotency and bounded runtime matter. Batch coverage cleanup must not overlap active aggregation. The monthly coverage report schedule encodes a 9-day propagation assumption with a 15-day conservative trigger. Missing handler registration would surface only at runtime.

Test signals: no direct test for `cron.yaml` in this subset. Its coverage is indirect through tests of the handlers it triggers, such as cache, asset deprecation, coverage, and dungeon preheat logic.
