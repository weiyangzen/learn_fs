# sources/test-tools/syzkaller/dashboard/app/api.go

## Purpose

`api.go` is the main App Engine dashboard API dispatcher and a large set of handlers for syzkaller manager, reporting, bug, build, crash, repro, asset, email, upload, and coverage operations. It also defines authentication/namespace enforcement wrappers that every `/api` method uses.

## Important APIs and functions

- API setup and wrappers: `initAPIHandlers`, `apiHandlers`, `handleJSON`, `handleAPI`, `gcsPayloadHandler`, `nsHandler`, `globalHandler`, `anyHandler`, and `typedHandler`.
- Authentication and context: `APIContext`, `apiContext`, and `checkClient`.
- Build/commit paths: `apiBuilderPoll`, `apiCommitPoll`, `apiUploadCommits`, `addCommitInfo`, `apiUploadBuild`, `uploadBuild`, `addCommitsToBugs`, and manager update helpers.
- Crash/bug paths: `apiReportBuildError`, `apiReportCrash`, `reportCrash`, `saveCrash`, `purgeOldCrashes`, `findExistingBugForCrash`, `findBugForCrash`, `createBugForCrash`, `apiBugList`, `apiLoadBug`, `apiLoadFullBug`, and `loadBugReport`.
- Repro paths: `apiReportFailedRepro`, `saveFailedReproLog`, `saveReproAttempt`, `apiNeedRepro`, `needRepro`, `apiLogToReproduce`, `saveReproTask`, `loadReproTasks`, `takeReproTask`, and `apiReproTaskDone`.
- Text/asset utilities: `putText`, `getText`, `parseIncomingAsset`, `parseCrashAssets`, `apiAddBuildAssets`, and `apiNeededAssetsList`.
- Miscellaneous handlers: `apiManagerStats`, `apiUpdateReport`, `apiSaveDiscussion`, `recordEmergencyStop`, `emergentlyStopped`, `apiCreateUploadURL`, `apiSendEmail`, and `apiSaveCoverage`.

## Control flow and state behavior

`handleAPI` reads `client`, `method`, and `key` form values, derives an OAuth subject from the `Authorization` header, validates the client through `checkClient`, installs an `APIContext`, optionally ungzips the form `payload`, dispatches to `apiHandlers`, and verifies that handlers used the correct namespace wrapper. `nsHandler` rejects global clients for namespace-only methods; `globalHandler` rejects namespace clients for global methods; `anyHandler` marks namespace checking complete for methods allowed in either context.

Build uploads validate string lengths, parse assets, store kernel configs in compressed text entities, put `Build` entities in datastore, update current manager build state, and associate fix commits with bugs. Crash reports are gated by emergency stop, build existence, namespace transforms, canonicalized titles, existing bug lookup, optional new bug creation, crash saving, subsystem inference, and transactional bug counter updates. Text blobs are gzip-compressed and sometimes deduplicated by hash, with large crash logs truncated until compressed data fits datastore limits.

Repro and reporting handlers mutate datastore entities such as `Bug`, `Crash`, `Build`, `Manager`, `EmergencyStop`, `Text`, and `ReproTask`. Coverage upload is the main streaming/GCS path: the handler accepts a GCS URL payload, opens and ungzips the object, decodes JSONL records, and writes to `coveragedb`.

## Dependencies and integration points

The file integrates App Engine datastore, mail, user, and logging APIs; `dashapi` wire types; auth token validation; gzip/JSON payload transport; GCS; coverage database writes; crash asset metadata; subsystem inference; email address merging; syzkaller target metadata; and dashboard config. It is also the central integration point for AI methods registered in `apiHandlers`, although many AI-specific handler bodies live in other files.

## Risks and edge cases

The dispatcher has security-sensitive namespace checking: every handler must go through the correct wrapper or `handleAPI` returns an error. `checkClient` uses constant-time comparisons for API keys and OAuth magic subjects, but method allowlists and namespace lookup must remain correct. Crash reporting has many datastore transaction boundaries; stale reads are rechecked inside transactions for updates. `putText` truncates and recompresses large payloads, which preserves storage limits but can drop leading log data. `takeReproTask` knowingly avoids strict transactional claiming, so duplicate repro attempts are possible but bounded. Emergency stop blocks new crash/job intake but must be consistently checked by handlers that create externally visible work.

## Test signals

`api_test.go` covers credential and namespace enforcement, emergency stop behavior, reporting priority, and upload URL format. `app_test.go` covers end-to-end build/crash/reporting paths, crash purging, failed build manager state, status codes, and linkification. Many additional dashboard test files outside this subset exercise handlers registered in `apiHandlers`.
