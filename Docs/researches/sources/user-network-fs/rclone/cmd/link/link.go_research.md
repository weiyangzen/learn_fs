# sources/user-network-fs/rclone/cmd/link/link.go

Purpose: implements `rclone link`, creating, retrieving, expiring, or removing public links for files or folders.

Important state/APIs: package globals `expire` and `unlink`; flags `--expire` and `--unlink`; Cobra `commandDefinition`. It calls `cmd.NewFsFile` to split remote path and `operations.PublicLink` to perform backend-specific public-link behavior.

Control flow: validates exactly one path, builds source filesystem plus remote leaf, then runs a non-mutating stats wrapper via `cmd.Run(false, false, ...)`. If `PublicLink` returns a non-empty link, it prints it as the final line.

State/persistence: no local persistence, but it may create or remove remote-side shared-link state depending on backend capabilities. Dependencies are `cmd`, `fs.Duration`, `operations`, Cobra. Risks center on backend capability differences, expiration support, and unlink being ignored by unsupported remotes. Tests are not in this subset; coverage is likely in backend/operations public-link tests.
