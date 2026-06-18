<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCrc32c.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdCrc32c.cc

Purpose: implements `xrdcrc32c`, a standalone utility that computes a CRC32C checksum for a local file or stdin and prints it in hexadecimal.

Important APIs/types/functions: `Fatal()` reports system errors and exits; `Usage()` prints CLI help; `main()` parses `-d`, `-h`, `-n`, `-s`, and `-x`, opens the input, allocates a page-aligned 1 MiB buffer, streams reads through `XrdOucCRC::Calc32C()`, and prints the checksum with optional path/newline formatting.

Control flow: options set `O_DIRECT`, output formatting, path inclusion, and newline inclusion. If the operand is absent or `-`, stdin is used. Otherwise the file is opened read-only. The loop updates `csVal` until EOF, then errors are checked and output is emitted.

State/persistence: no persistent state. It reads input data and writes checksum text to stdout.

Dependencies/integration: depends on `XrdOucCRC`, `XrdSysE2T`, POSIX `open/read`, `posix_memalign`, and page-size alignment. `O_DIRECT` is defined as zero on platforms that lack it.

Risks/test signals: direct IO can impose alignment and filesystem constraints even though the buffer is aligned; file offsets and read sizes are fixed at 1 MiB. The allocated buffer is not freed on error exits. Tests should cover stdin, file input, direct mode, no-newline/no-path/no-leading-zero formatting, read/open errors, empty files, and known CRC32C vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCrc32c.cc -->
