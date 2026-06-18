<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/dedupe/dedupe.go -->
# sources/user-network-fs/rclone/cmd/dedupe/dedupe.go

## Purpose

`dedupe.go` implements `rclone dedupe`, resolving duplicate names or duplicate hashes through interactive or selected policies.

## Important APIs, Types, and Functions

Package globals are `dedupeMode` and `byHash`. `init` registers `--dedupe-mode` and `--by-hash`. The command accepts optional mode plus remote path, parses positional mode through `dedupeMode.Set`, resolves the target Fs with `cmd.NewFsSrc`, warns if duplicate names are unsupported and `--by-hash` is absent, then calls `operations.Deduplicate`.

## Control Flow

It runs without retries or stats. Mode parsing happens before Fs operation. The operation layer handles listing, duplicate grouping, prompts, deletes, and renames.

## State and Persistence Behavior

This command can delete or rename remote objects and merge duplicate directories. It creates no local persistent files.

## Dependencies and Integration Points

It integrates with backend `DuplicateFiles` feature signaling, operations dedupe modes, global dry-run/interactive behavior, and Fs helpers.

## Risks and Test Signals

Risks include data loss, interactive prompt deadlocks in automation, hash-less backends, duplicate directory merge semantics, and positional mode ambiguity. Tests should cover every dedupe mode, `--by-hash`, unsupported duplicate names, dry-run, hash-none behavior, and conflict/rename outcomes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/dedupe/dedupe.go -->
