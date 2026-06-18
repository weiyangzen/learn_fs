# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/main.c

Implements the main SMB1 server loop and request/response header handling for `cifsd`.

Key points:
- Defines NetBIOS session header length, SMB magic constants, SMB flags, flags2, capability-related flags, and case-sensitivity behavior.
- `respond` converts NT status to DOS error if needed, builds an SMB response header, zeroes signatures except for session setup, writes the NetBIOS length prefix, and sends to stdout.
- `receive` decodes SMB headers, rejects non-SMB1 magic including SMB2/3, chooses ASCII vs Unicode `Rop` packers, sets request metadata and name comparator, and dispatches via `smbcmd`.
- `serve` reads a byte stream from stdin, reassembles NetBIOS-framed SMB messages, and calls `receive` for each complete message.
- Command-line options:
  - `-t` disables authentication requirement.
  - `-d` increases debug.
  - `-f log` logs to a file.
  - `-w domain` sets workgroup/domain.
  - `-o trspaces` or `-o casesensitive` toggles options.
- Closes stderr and redirects it to the log or `/dev/null`.
- Initializes remote system, buffer size, start time, pid-based PRNG seed, timezone offset, logs startup/exit, serves, then logs off.

Dependencies and interactions:
- Uses `pack`, `unpack`, SMB string/name packers, `smbcmd`, `logoff`, and utility logging/remote functions.
- This file only handles protocol framing and dispatch; command implementations live elsewhere.

Research relevance:
- Main entry point and wire framing layer for the SMB1/CIFS server.
