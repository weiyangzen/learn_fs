# sources/sync-backup/kopia/internal/mount/mount_unsupported.go

Purpose: build-tag fallback for platforms without a supported mount implementation.

Important APIs/types/functions: `Directory` has the same signature as supported platform files and returns a clear unsupported error.

Control flow: immediately returns nil controller and an error mentioning unsupported OS/filesystem mounting.

State and persistence behavior: no state.

Dependencies and integration points: ensures callers can compile on unsupported platforms while receiving runtime failure.

Risks and test signals: callers must surface this error rather than assuming mounts always work. Build-tag validation should ensure only one `Directory` implementation is selected per target.
