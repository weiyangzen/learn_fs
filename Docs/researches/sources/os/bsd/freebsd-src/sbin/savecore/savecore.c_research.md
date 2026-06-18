# File Research: sources/os/bsd/freebsd-src/sbin/savecore/savecore.c

## Summary
Implements `savecore`, the crash-dump saver/checker/clearer and live-kernel-dump capture utility. It validates kernel dump headers, copies or decompresses dumps into a crash directory, manages bounds and symlinks, preserves encrypted dump keys, checks free space, and runs in Capsicum capability mode.

## Main Responsibilities
- Parses modes for checking dumps, clearing dumps, saving dumps, preserving headers, forcing bad dumps, live dumps, max dump rotation, verbosity, compression, and decompression.
- Enumerates dump devices from `fstab` swap/dump entries or explicit device arguments.
- Reads and validates first/last kernel dump headers, magic values, versions, parity, and compression metadata.
- Handles regular dumps, compressed dumps, encrypted dumps with key files, text dumps written backward, and live dumps via `MEM_KERNELDUMP`.
- Writes `info.N` metadata using libxo and optionally prints headers to stdout.
- Maintains `bounds`, `*.last` symlinks, and cleanup of existing dump files for reused bounds.
- Checks available crash-directory space against `minfree`.
- Uses sparse writes for uncompressed dump data.
- Supports gzip and zstd decompression of kernel-compressed dumps.
- Enters Capsicum mode with limited directory and device capabilities.

## Key Elements
- `DoFile()`: main dump-device path for normal crash dumps.
- `DoLiveFile()`: invokes live dump creation through `/dev/mem`, validates header, truncates trailing header, and renames the temporary file.
- `DoRegularFile()` / `DoTextdumpFile()`: copy/decompress/sparsify dump payloads.
- `GunzipWrite()` / `ZstdWrite()`: streaming decompression into sparse output.
- `check_space()`: enforces crash-directory free-space policy.
- `write_header_info()`, `printheader()`: libxo dump metadata output.
- `init_caps()`: Casper/fileargs/syslog setup and capability-mode transition.

## Dependencies And Integration
Uses kernel dump ABI headers, disk ioctls, `/etc/fstab`, `/var/crash` files, libxo, zlib, zstd, Casper `fileargs`, Casper syslog, and Capsicum helpers.

## Research Notes
The code treats dump validity and dump preservation separately: bad headers/parity normally stop saving, but `-f` can force some cases; `-k` preserves the dump header, while the default clears it after processing.
