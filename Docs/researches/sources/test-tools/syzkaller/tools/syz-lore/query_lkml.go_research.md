# sources/test-tools/syzkaller/tools/syz-lore/query_lkml.go

## Purpose
`syz-lore` parses LKML/lore archive directories, extracts syzbot-related email threads, and saves them either as JSON discussion files or through the syzkaller dashboard API.

## Important APIs, types, and functions
- Flags configure own emails/domains, output directory, dashboard endpoint/client/key, and verbose logging.
- `main` validates archive arguments, calls `processArchives`, converts `lore.Thread` objects to `dashapi.Discussion`, and persists each discussion.
- `saveDiscussion` lazily creates a global `dashapi.Dashboard`, writes JSON files named by `hash.String(d.ID)`, and/or calls `Dashboard.SaveDiscussion`.
- `processArchives` concurrently reads LKML repositories through `vcs.NewLKMLRepo` and `lore.ReadArchive`, parses messages with `lore.Parse`, groups them with `lore.Threads`, and filters to threads with syzbot bug IDs.

## Control flow
Archive paths are read by errgroup jobs that enqueue `lore.EmailReader` values on a channel. A worker pool sized to `runtime.NumCPU()` consumes that channel, reads raw messages, parses them, strips body/patch payloads, and appends metadata under a mutex. After archive readers finish, the channel closes, parsing errors are counted and skipped, and grouped threads are filtered before returning.

## State and persistence behavior
State is mostly in memory: `repoEmails`, skipped parse count, and the global dashboard client. Persistent side effects are JSON discussion files under `-out_dir` and remote dashboard writes when dashboard flags are set. Email body and patch content are cleared before storing to reduce output size and sensitivity.

## Dependencies and integration points
The tool depends on `pkg/email/lore` for archive parsing/threading, `pkg/vcs` for LKML archive access, `dashboard/dashapi` for persistence, `pkg/hash` for stable filenames, and `pkg/tool` for initialization/fatal errors. It integrates with syzbot dashboard discussion ingestion.

## Risks and edge cases
The goroutine closure over `path` relies on Go range semantics; older Go versions would risk capturing the wrong path. `strings.Split("", ",")` yields a single empty string for unset email/domain flags, so downstream parsing must tolerate empty identifiers. Broken LKML messages are silently skipped except for a count, which is pragmatic but can hide archive quality regressions. Dashboard and JSON writes are sequential after concurrent parsing.

## Test signals
No local tests in this file. Behavioral confidence comes from `lore` and `dashapi` package tests and from manual runs over real archives. Useful test cases would include malformed email handling, filtering threads without bug IDs, JSON output naming, and simultaneous dashboard plus local output.
