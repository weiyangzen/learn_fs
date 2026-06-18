# sources/user-network-fs/samba/source3/modules/vfs_virusfilter_sophos.c

## Purpose
This file implements the Sophos SAVDI SSSP/1.0 backend for `vfs_virusfilter`. It connects to the SAVDI socket, configures SSSP options, URL-quotes file paths, sends `SCANFILE`, and converts SSSP replies into core scan results.

## Important APIs, Types, and Functions
`virusfilter_url_quote()` percent-encodes path characters for SSSP. `virusfilter_sophos_connect()` sets CRLF read EOL handling. `virusfilter_sophos_scan_ping()` sends an `OPTIONS` request to validate an existing connection. `virusfilter_sophos_scan_init()` connects to the default `/var/run/savdi/sssp.sock` or configured socket, validates `OK SSSP/1.0`, and configures `output:brief` plus archive scanning. `virusfilter_sophos_scan()` sends `SSSP/1.0 SCANFILE <encoded path>`, expects `ACC`, then reads records until a blank line. `VIRUS` marks infected; `DONE` codes other than known clean/infected codes mark scanner error.

## Control Flow
The core invokes scan init before scanning. If a stream exists, Sophos ping is attempted and a good stream is reused; otherwise the stream is closed and recreated. The scan path builds one encoded URL from current directory plus filename, writes the command without an explicit line helper, validates acceptance, then iterates response lines.

## State and Persistence
The backend stores no custom private state. The shared I/O stream and socket path are the only runtime state. Reports are allocated transiently for the core.

## Dependencies and Integration Points
It depends on Sophos SAVDI's SSSP/1.0 protocol and shared virusfilter socket helpers. It uses Samba's `nybble_to_hex_upper()` for encoding and the core's archive-scan flag.

## Risks
The URL quoting routine treats `char` bytes directly; signed-char high-bit handling can produce surprising encodings on non-ASCII filenames. The command write length is fixed and must match the literal prefix. Reply parsing assumes non-empty tokens. The backend reports only a single token after `VIRUS`, so multi-word scanner reports may be truncated.

## Test Signals
Protocol tests should cover greeting validation, options accepted/done/blank-line sequencing, connection reuse, long path failure, clean `DONE OK 0000`, infected `VIRUS` plus `DONE OK 0203`, scanner error codes, and malformed/empty replies.
