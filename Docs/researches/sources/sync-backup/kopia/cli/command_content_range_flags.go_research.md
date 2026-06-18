# sources/sync-backup/kopia/cli/command_content_range_flags.go

## Purpose
Shared flag parser for content ID ranges. It normalizes prefix/start/end options into a content iteration range used by list/show/delete/rewrite/verify commands.

## APIs, Types, and Functions
Important APIs include types `contentRangeFlags`; functions/methods `setup`, `contentIDRange`; flags prefix: Content ID prefix, prefixed: Apply to content IDs with (any) prefix, non-prefixed: Apply to content IDs without prefix.

## Control Flow, State, and Persistence
Control flow binds flags prefix: Content ID prefix, prefixed: Apply to content IDs with (any) prefix, non-prefixed: Apply to content IDs without prefix, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content indexes, pack blobs, and content metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports github.com/alecthomas/kingpin/v2, github.com/kopia/kopia/repo/content, github.com/kopia/kopia/repo/content/index. It integrates with Kopia repository internals such as kopia/repo/content, kopia/repo/content/index plus external packages github.com/alecthomas/kingpin/v2.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
