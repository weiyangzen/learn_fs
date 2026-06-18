# sources/sync-backup/syncthing/cmd/infra/ursrv/serve/serve.go

Purpose: implements the usage reporting server that accepts Syncthing client reports, enriches them, serves aggregate Prometheus metrics, and periodically persists report dumps locally and optionally to S3-compatible blob storage.

Important APIs/types/functions: `CLI`, `knownDistributions`, `distributionMatch`, `CLI.Run`, `downloadDumpFile`, `saveDumpFile`, `server`, `handleNewData`, `addReport`, `save`, `load`, and `transformVersion`.

Control flow: `Run` opens external and internal listeners, optionally starts GeoIP, optionally opens S3 storage and downloads the latest dump, loads a gzip JSON-lines dump into an `xsync` map, starts periodic dump writes/uploads, exposes internal process metrics on `/metrics`, registers a custom usage metrics registry on the external `/metrics`, and handles `/newdata` and `/ping`. `handleNewData` accepts only POST, derives IP from `X-Forwarded-For` or `RemoteAddr`, limits body reads to 40 KiB, validates a `contract.Report`, stamps received/date/address fields, and stores it by unique ID. `addReport` enriches country, major version, OS/arch, compiler, builder, distribution, and database backend flags.

State and persistence: live reports are held in `xsync.MapOf[string,*contract.Report]`. Persistence is gzip-compressed JSON-lines in `DumpFile`, atomically written via `.tmp` rename, with optional daily S3 object upload. On startup, an absent local dump can be restored from latest blob key.

Dependencies/integration: depends on `contract.Report` validation, GeoIP, `blob`/S3, Prometheus, Suture supervisor for metrics recalculation, `slog`, and Syncthing build/version conventions.

Risks and test signals: reports are keyed by `UniqueID`, so repeat reports replace older ones. Body truncation can cause decode failure for oversized reports. `metricsWriteSecondsLast.Set(float64(time.Since(t0)))` records nanoseconds as a float despite the metric name saying seconds. `handlePing` intentionally returns an empty 200. Tests in this subset cover only `compilerRe`.
