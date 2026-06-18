# sources/sync-backup/kopia/cli/command_policy_edit.go

## Purpose
Policy edit command that opens an existing snapshot policy as pretty JSON with embedded help text, launches an editor, validates JSON changes, and persists updates if modified.

## APIs, Types, and Functions
Important APIs include types `commandPolicyEdit`; functions/methods `setup`, `run`, `prettyJSON`, `jsonEqual`, `insertHelpText`; Kingpin command(s) edit: Edit policy..

## Control Flow, State, and Persistence
Control flow registers command(s) edit: Edit policy., then runs through a repository writer action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches snapshot policy manifests. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports bytes, context, encoding/json, fmt, strings, github.com/pkg/errors, github.com/kopia/kopia/internal/editor, github.com/kopia/kopia/repo, github.com/kopia/kopia/snapshot/policy. It integrates with Kopia repository internals such as kopia/internal/editor, kopia/repo, kopia/snapshot/policy plus external packages bytes, context, encoding/json, fmt, strings, plus 1 more.

## Risks and Test Signals
Risks and test signals: external editor flow must reject invalid or unchanged JSON safely. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
