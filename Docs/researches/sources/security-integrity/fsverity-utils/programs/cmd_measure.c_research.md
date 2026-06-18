# sources/security-integrity/fsverity-utils/programs/cmd_measure.c

Purpose: This command asks the kernel to measure a verity-enabled file and prints the kernel-reported digest.

Important APIs and functions: `fsverity_cmd_measure()` opens the file, prepares `struct fsverity_digest`, calls `FS_IOC_MEASURE_VERITY`, and formats the digest algorithm and bytes for output.

Control flow and state: It has a simple parse/open/ioctl/print flow. Runtime state is the opened file and digest buffer; persistent state is read-only kernel metadata on the file.

Dependencies and integration points: Used to compare kernel-measured digests with `cmd_digest`/library-computed digests. Depends on fs-verity UAPI and shared CLI utilities.

Risks and test signals: Kernel support and file state dominate failures. The command must handle unsupported files, digest buffer sizing, and output format compatibility. Signals include matching computed and measured digest for enabled files and expected errors for non-verity files.
