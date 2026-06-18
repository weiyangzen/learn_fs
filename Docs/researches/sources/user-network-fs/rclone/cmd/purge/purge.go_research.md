# sources/user-network-fs/rclone/cmd/purge/purge.go

Purpose: implements `rclone purge`, deleting a path and all of its contents without obeying include/exclude filters.

Important API: Cobra `commandDefinition`; uses `cmd.NewFsDir` and `operations.Purge`.

Control flow: validates one remote path, creates directory Fs, then runs in a mutating command context. Before deletion it checks `filter.GetConfig(ctx).InActive()` and fatals if include/exclude filters are active, making the unconditional purge behavior explicit, then calls `operations.Purge(context.Background(), fdst, "")`.

State/persistence: destructive remote mutation; deletes objects/directories under the target. Dependencies are command root and operations. Risks are obvious data loss, filter bypass by design, and backend purge semantics. Test signal is mostly operations/backend integration.
