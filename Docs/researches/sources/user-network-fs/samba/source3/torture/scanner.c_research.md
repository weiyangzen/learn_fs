# sources/user-network-fs/samba/source3/torture/scanner.c

## Purpose
`scanner.c` probes SMB `TRANS2` and `NTTRANS` subcommands/info levels to discover accepted parameter formats, minimum data lengths, and non-obvious server responses.

## Important APIs, types, and functions
For `TRANS2`, key functions are `try_trans2`, `try_trans2_len`, `scan_trans2`, and `torture_trans2_scan`. For `NTTRANS`, analogous functions are `try_nttrans`, `try_nttrans_len`, `scan_nttrans`, and `torture_nttrans_scan`. `trans2_check_hit` and `nttrans_check_hit` filter common negative statuses.

## Control flow
Each exported test opens a connection, creates or opens `\scanner.dat` and a root directory handle, then loops operations `OP_MIN..OP_MAX` and level ranges `0..50`, `0x100..0x130`, and `1000..1049`. For each pair it tries several parameter shapes: info level alone, file handle, notify-style handles, existing filename, new filename, and DFS-style directory path. If a full-size request succeeds, it searches for the minimum data length that also succeeds and prints the hit.

## State and persistence behavior
The scanner creates temporary names such as `\scanner.dat`, `\newfile.dat`, and `\testdir`. It attempts cleanup after new-file and DFS probes, but the scanner is exploratory and may leave artifacts if interrupted.

## Dependencies and integration points
It uses low-level `cli_trans` over `SMBtrans2` and `SMBnttrans`, Unicode-aware `trans2_bytes_push_str`, and `torture_open_connection`. It is registered in the torture harness as trans2 and nttrans scan tests.

## Risks and test signals
This is a fuzz-like protocol scanner, not a strict conformance test. Positive prints indicate implemented or partially accepted levels; unusual statuses may suggest parser bugs. It can exercise server code paths with malformed parameter/data lengths, so it is useful for robustness testing but can be noisy.
