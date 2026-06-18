# sources/security-integrity/gocryptfs/contrib/statfs/statfs.go

Purpose: This small diagnostic prints `statfs` information for a path as JSON.

Important APIs and functions: `main` parses exactly one path, calls `unix.Statfs`, marshals `unix.Statfs_t` with `json.MarshalIndent`, and prints it.

Control flow and state: The command is read-only and exits with usage or syscall errors. It persists no state.

Dependencies and integration points: Useful for inspecting gocryptfs/FUSE filesystem statfs passthrough and comparing with backing filesystems.

Risks and test signals: Linux/Go struct fields can vary by platform. Signals are successful JSON output and meaningful syscall errors for invalid paths.
