# sources/test-tools/syzkaller/pkg/email/lore/read.go

Purpose: `lore/read.go` adapts the syzkaller vcs abstraction to the email lore parser by exposing commit-backed email readers.

Important APIs/types/functions: `EmailReader` embeds `vcs.CommitShort` and supplies a `Read` closure. `ReadArchive` lists recent commits and returns one reader per commit. `Email` wraps `*email.Email` with `HasPatch`. `Parse` parses raw bytes through the base email parser and records whether a patch was present.

Control flow and state: `ReadArchive` calls `repo.LatestCommits(afterCommit, afterTime)`, captures each loop variable safely, and defines `Read` to fetch object `m` at the commit hash. `Parse` uses no mailing-list whitelist, accepts caller-provided own emails and domains, and computes `HasPatch` from `msg.Patch != ""`.

Dependencies and integration: this file bridges `pkg/vcs`, `pkg/email`, and the lore grouping/poller code. The convention that each archive commit stores message content as object `m` is central.

Risks: archive shape is assumed; if the LKML repo layout changes, `repo.Object("m", hash)` fails. `HasPatch` depends on the heuristic `email.ParsePatch`. Tests exercise this through lore parse and poller scenarios.
