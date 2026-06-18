# sources/user-network-fs/samba/source4/torture/basic/scanner.c

## Purpose
This file implements exploratory scanners for TRANS2, NTTRANS, and base SMB opcodes. It discovers which opcodes and information levels elicit meaningful responses from a server.

## Important APIs, types, and functions
TRANS2 helpers are `trans2_check_hit()`, `try_trans2()`, `try_trans2_len()`, `trans2_op_exists()`, `scan_trans2()`, and exported `torture_trans2_scan()`. NTTRANS helpers are `nttrans_check_hit()`, `try_nttrans()`, `try_nttrans_len()`, `scan_nttrans()`, and exported `torture_nttrans_scan()`. Base opcode scanning is in `torture_smb_scan()`. It uses `struct smb_trans2`, `struct smb_nttrans`, `DATA_BLOB`, `SSVAL`, `push_string()`, and raw SMB request setup/send/process APIs.

## Control flow
TRANS2 scanning first creates/open handles for a test file, root directory, and quota stream. It checks whether each op differs from a known invalid op, then probes levels `0..50`, `0x100..0x130`, and `1000..1049` using multiple parameter shapes: info-level-only, file descriptor, quota descriptor, notify-style descriptor, existing filename, new filename, and DFS-style directory name. NTTRANS follows the same level ranges without the quota case. Base SMB scanning opens a fresh connection for each opcode except `SMBreadbraw`, sends a minimal request, waits briefly, prints status or no-reply, and avoids closing a connection that did not reply.

## State and persistence
The scanners create `\scanner.dat`, `\newfile.dat`, and `\testdir` transiently, but cleanup is incomplete for `\scanner.dat` and open handles. Most state is temporary talloc memory and raw request buffers.

## Dependencies and integration points
This is a low-level compatibility discovery tool over Samba's raw SMB APIs. It depends on dialect behavior, server validation paths, and configured access to quota/DFS-like paths. Output is printed rather than asserted.

## Risks
The scanners send intentionally malformed or broad requests and can trigger server log noise, slow paths, or disconnects. The base SMB scanner may leave a connection open on no-reply paths by design. Results are discovery data, not deterministic pass/fail guarantees.

## Test signals
Signals are printed `Found op`, `found <format> level=...`, base opcode status lines, no-reply cases, and unexpected non-generic statuses that survive the ignore filters.
