<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cachestats/cachestats.go -->
# sources/user-network-fs/rclone/cmd/cachestats/cachestats.go

## Purpose

This build-tagged command keeps the deprecated `rclone cachestats` entry point available on supported platforms. It prints JSON cache backend statistics for a `backend/cache` remote and directs users toward the newer `rclone backend stats` path.

## Important APIs, Types, and Functions

`init` registers `commandDefinition` on `cmd.Root`. The Cobra command validates one `source:` argument, builds an Fs with `cmd.NewFsSrc`, unwraps through `Features().UnWrap` when needed, requires a `*cache.Fs`, calls `Stats`, and formats the resulting map with `json.MarshalIndent`.

## Control Flow

The command emits a deprecation log, enters `cmd.Run` without retries or stats, resolves the source, rejects non-cache remotes, marshals stats, and writes to stdout.

## State and Persistence Behavior

It does not mutate the remote. It reads in-memory or backend-owned cache state and produces transient stdout output.

## Dependencies and Integration Points

It integrates with Cobra command registration, the rclone root command helpers, `backend/cache`, Fs feature unwrapping, and JSON output.

## Risks and Test Signals

Risks are stale compatibility with a deprecated backend, type assertion failures through wrappers, and unsupported-platform build behavior. Tests should cover direct cache Fs, wrapped cache Fs, non-cache errors, JSON marshal shape, and deprecation visibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cachestats/cachestats.go -->
