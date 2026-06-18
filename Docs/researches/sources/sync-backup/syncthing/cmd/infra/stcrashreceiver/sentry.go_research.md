# sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/sentry.go

Purpose: Sentry integration for crash reports and failure reports. It parses Go panic dumps into Sentry packets with stack traces, tags, source context, fingerprints, and user identity.

Important APIs/types/functions: global `loader`, `clients` map and mutex; `sentryService`, `sentryRequest`, methods `Serve` and `Send`; functions `sendReport`, `parseCrashReport`, `sanitizeMessageLDB`, `crashReportFingerprint`, and `packet`. Regexes normalize indexes, sizes, LevelDB positions/checksums/files/internal keys, and local LevelDB paths.

Control flow: `Serve` consumes queued crash reports, parses them, sends to Sentry, and updates result metrics. `parseCrashReport` splits first version line, finds panic/fatal subject, uses `panicparse` to scan goroutines, locks source loader to commit/tag/main, creates reversed Sentry stack frames from the first goroutine, adds report URL, and sets fingerprint. `sendReport` caches Sentry clients per DSN and copies release/environment onto the client before capture.

State and persistence behavior: in-memory Sentry client cache, source-loader lock/cache, and queue. No disk writes here.

Dependencies/integration: raven-go, panicparse, Syncthing build version parsing, sourcecodeloader, crashreceiver HTTP storage, metrics, and Sentry grouping rules.

Risks/test signals: global loader locking serializes source-context loading per parsed report. Empty DSN or Sentry errors surface as send failures. Fingerprint sanitation is crucial to avoid over-splitting corruption reports. Tests cover parsing sample logs and fingerprint normalization.
