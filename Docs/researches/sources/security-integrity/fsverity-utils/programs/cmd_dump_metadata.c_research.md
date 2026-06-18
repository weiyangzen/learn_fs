# sources/security-integrity/fsverity-utils/programs/cmd_dump_metadata.c

Purpose: This CLI command dumps fs-verity metadata from a verity-enabled file using the kernel `FS_IOC_READ_VERITY_METADATA` ioctl.

Important APIs and functions: `parse_metadata_type()` maps names `merkle_tree`, `descriptor`, and `signature` to UAPI constants. `fsverity_cmd_dump_metadata()` parses optional `--offset` and `--length`, opens the file, repeatedly calls the ioctl, and writes raw metadata to stdout.

Control flow and state: Without explicit offset/length, the command loops until ioctl returns zero bytes. With offset/length, it performs one bounded read. State is limited to the ioctl arg, buffer, file descriptor, and stdout descriptor wrapper.

Dependencies and integration points: Uses `fsverity_uapi.h`, shared `open_file`, `full_write`, and command dispatch.

Risks and test signals: Risks include raw binary stdout handling, offset/length validation, and kernel support differences. Signals include successful descriptor/tree/signature dumps and usage errors for malformed metadata type or incomplete offset/length pairs.
