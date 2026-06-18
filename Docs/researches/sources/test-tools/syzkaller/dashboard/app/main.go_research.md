# sources/test-tools/syzkaller/dashboard/app/main.go

## Purpose

`main.go` is the primary web UI handler and view-model assembly file for the syzkaller dashboard App Engine application. It registers public, namespace-scoped, admin, text, coverage, subsystem, manager, bug, AI, and cron routes through `initHTTPHandlers`, then implements the bulk of dashboard page controllers and UI DTO construction for templates and optional JSON output.

## Important APIs, Types, and Functions

The file defines many `ui*` structs consumed by templates and the public JSON adapter: `uiMainPage`, `uiBugFilter`, `uiManagerList`, `uiTerminalPage`, `uiBugStats`, `uiReposPage`, `uiSubsystemPage`, `uiSubsystemsPage`, `uiAdminPage`, `uiManagerPage`, `uiBugPage`, `uiBugDetails`, `uiBugGroup`, `uiBug`, `uiCrash`, `uiBuild`, `uiJob`, `uiBackportsPage`, and related small structs. These isolate datastore entities from rendered pages and allow access-sensitive fields to be removed or transformed.

Core handlers include `handleMain`, `handleFixed`, `handleInvalid`, `handleManagerPage`, `handleSubsystemPage`, `handleBackports`, `handleRepos`, `handleTerminalBugList`, `handleAdmin`, `handleBug`, `handleBugSummaries`, `handleSubsystemsList`, and `handleTextImpl`. Helper functions such as `MakeBugFilter`, `userBugFilter.MatchBug`, `fetchNamespaceBugs`, `prepareBugGroups`, `loadVisibleBugs`, `fetchTerminalBugs`, `createUIBug`, `loadCrashesForBug`, `makeUICrash`, `makeUIBuild`, `loadManagers`, and `makeUIJob` form the main data pipeline.

## Control Flow

Requests enter App Engine through `handlerWrapper` routes. Namespace pages build a `uiHeader`, parse filters, fetch managers and bugs, then group bugs by reporting stage. Bug detail pages load one bug by datastore ID or reporting extid, enforce access, assemble crashes, duplicate/similar bugs, bisection jobs, discussions, test results, AI jobs, labels, and patch versions, and render either `bug.html` or `GetJSONDescrFor` output. Terminal pages reuse the same filtering but select fixed or invalid bugs. Admin pages enforce `AccessAdmin`, optionally perform actions, and then use `errgroup` to fetch memcache stats, managers, logs, and job lists concurrently.

Text endpoints parse legacy decimal IDs or newer hex `x` IDs, call access checks, load blob-like text entities, add reproducer headers when needed, and stream plain text. Backports aggregate cross-tree fix candidate jobs by source/target repository and commit. Subsystem pages use the namespace subsystem service, redirect renamed subsystems, and show child/parent subsystem data plus bug groups.

## State and Persistence Behavior

This file mostly reads from datastore-backed helpers: bugs, crashes, builds, managers, jobs, repro tasks, reporting state, cached UI pages, subsystem cache, AI DB records, text entities, and Google Cloud logs. It writes state only in controller actions such as saving manager repro tasks, creating AI jobs, forcing manual patch iteration, admin actions, and indirectly through helper calls. It also reads memcache stats and may flush memcache from the admin page. Cached UI paths are used when no filters are active and the namespace enables page caching.

## Dependencies and Integration Points

The code integrates with App Engine datastore, memcache, user/admin identity, Cloud Logging, syzkaller dashboard config, reporting logic, discussion storage, asset storage, subsystem inference, AI patching data, coverage handlers, job/bisection helpers, and template rendering. It also delegates public JSON conversion to `public_json_api.go` through `writeJSONVersionOf`.

## Risks and Edge Cases

The file has a wide blast radius: filter behavior affects both pages and JSON, access checks must remain consistent with sanitized bug/reporting data, and datastore query constraints shape filter implementation. The `userBugFilter` applies only the first label at query level and then filters remaining labels in memory, so performance depends on result sizes. `loadVisibleBugs` runs duplicate and open bug queries in parallel and then merges dup bugs later; changes can easily hide duplicates or expose inaccessible bugs. Text serving is sensitive because it exposes logs, reproducers, configs, and reports and relies on `checkTextAccess` plus namespace access checks. Admin actions are high privilege and dispatch to many mutating helpers. Cloud log fetching uses an explicit filter with many exclusions; changes may flood or hide admin diagnostics.

## Test Signals

`main_test.go` directly covers manager-only filtering, subsystem and label filters, subsystem list/page behavior, admin job list links, subsystem redirects, throttling, manager page build filtering, and repro form access. `public_json_api_test.go` exercises the JSON path that starts from `handleBug`, `handleMain`, and terminal pages. Other dashboard tests indirectly cover bug/job/reporting helpers used here.
