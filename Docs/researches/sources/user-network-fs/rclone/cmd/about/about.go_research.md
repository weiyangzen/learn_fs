# sources/user-network-fs/rclone/cmd/about/about.go

Purpose: implements `rclone about remote:` for printing backend quota/usage information. It registers a Cobra command with `--json` and `--full` flags, creates a source Fs, invokes the backend `Features().About` optional interface, and formats `fs.Usage` fields.

Important functions: `printValue` handles nil values, byte/count formatting, and full numeric output; the command `Run` wraps execution through `cmd.Run`, checks backend support, handles nil usage, and either JSON-encodes with indentation or prints Total/Used/Free/Trashed/Other/Objects. State is read-only against the remote. Dependencies are `fs.Abouter`, `fs.Usage`, command flag helpers, and Cobra. Risks include unsupported backends, partial usage fields, backend-specific stale quota, and global package flags in tests. Test signal is likely command integration elsewhere; this file has no local unit test.
