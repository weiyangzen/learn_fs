# File Research: sources/virtualization/nbdkit/plugins/iso/iso.c

This plugin creates a temporary ISO image from one or more directories and serves it read-only over NBD.

Configuration:
- Requires at least one `dir`.
- `prog` overrides the ISO creation tool selected at compile time.
- `params` appends extra arguments to the ISO creation command.

Image creation:
- `.get_ready` calls `make_iso`.
- Creates a temporary file under `$TMPDIR` or `LARGE_TMPDIR`, then unlinks it.
- Builds a shell command with `shell_quote` for program and directories.
- Uses xorriso `-as mkisofs` when compiled for xorriso.
- Redirects ISO command output to the temp fd.
- Uses `exit_status_to_nbd_error` for command result mapping.

NBD behavior:
- `.get_size` uses `device_size` on the temp fd.
- `.block_size` prefers 2048 bytes to resemble CD media.
- `.can_multi_conn` is true.
- `.can_cache` asks nbdkit to emulate cache via reads.
- `.pread` loops on `pread` from the temp fd.

Risks:
- `params` is appended raw, intentionally allowing user-supplied command parameters but requiring trust.
- Requires external ISO tooling.
- Temporary ISO is fixed at `.get_ready`; source directory changes after that are not reflected.
