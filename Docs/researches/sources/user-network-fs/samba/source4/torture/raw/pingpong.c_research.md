# sources/user-network-fs/samba/source4/torture/raw/pingpong.c

## Purpose
This file implements `torture_ping_pong()`, a long-running byte-range-lock coordination benchmark. Multiple clients can run against the same file and lock ring, passing exclusive ownership from byte offset to byte offset. Optional reads and writes make each participant observe and advance per-slot counters while lock throughput is reported once per second.

## Important APIs, types, and functions
Local helpers are `lock_byte()`, `unlock_byte()`, `write_byte()`, and `read_byte()`. The exported entry point is `torture_ping_pong()`. The code uses `union smb_lock`, `struct smb_lock_entry`, `union smb_write`, `union smb_read`, `RAW_LOCK_LOCKX`, `LOCKING_ANDX_LARGE_FILES`, `RAW_WRITE_WRITEX`, `RAW_READ_READX`, `smb_raw_lock()`, `smb_raw_write()`, `smb_raw_read()`, `smbcli_open()`, `torture_open_connection()`, and torture settings accessors.

## Control flow
`torture_ping_pong()` requires `torture:filename` and `torture:num_locks` settings. It also reads `read`, `write`, and `lock_timeout`, defaulting to no reads/writes and a 100-second lock timeout. It opens one SMB connection and creates or opens the selected file read/write. It writes a zero byte at offset `num_locks` to establish file length, then locks byte zero.

The main loop advances index `i` around the ring. For each slot it locks `(i + 1) % num_locks`, optionally reads byte `i` and computes how much that byte changed since this process last saw it, optionally writes `val[i] + 1` to byte `i`, then unlocks byte `i`. This creates a handoff where the next byte is locked before the current byte is released. Once per second it prints `2 * count / elapsed` as locks per second because each loop iteration performs one lock and one unlock.

`lock_byte()` sends a single large-file LockingX lock. If `lock_timeout` is zero, file-lock conflicts and lock-not-granted statuses are handled by busy retrying until the lock succeeds. Otherwise the server-side timeout is used and any non-OK result exits the process. `unlock_byte()` sends a single unlock with a fixed 100-second timeout. `write_byte()` and `read_byte()` perform one-byte raw write/read operations and exit on failure.

## State and persistence
Server state is the user-specified shared file and byte-range locks over offsets `0..num_locks-1`. If writes are enabled, each byte stores a modulo-256 counter updated by whichever process currently owns that slot. Local state includes a talloc-allocated `val[]` shadow array of last observed byte values, increment tracking, loop counters, and the current ring index. There is no cleanup path because this benchmark is designed to run until externally stopped.

## Dependencies and integration points
The test depends on a configured SMB torture target and externally coordinated settings so multiple processes use the same filename and lock count. It is modeled on `lockbench.c` and integrates only with the raw SMB client/torture utility layer. It assumes strict byte-range lock enforcement and uses `cli->tree->session->pid` as the lock owner PID.

## Risks
This is an infinite benchmark loop with `exit(1)` on helper failures, so it does not provide normal teardown. With `lock_timeout=0`, conflicting locks cause a busy retry loop that can consume CPU. Invalid `num_locks` values are only checked for missing `-1`; zero would lead to modulo-by-zero behavior in the main loop. Multiple participants must agree on file and lock count or the ring protocol becomes meaningless. Optional writes use byte counters and naturally wrap at 255.

## Test signals
Operational signals are sustained locks-per-second output, periodic `data increment = N` changes when reads are enabled, absence of lock/unlock/read/write fatal messages, and coordinated progress among all participating clients. Failures indicate broken byte-range-lock conflict handling, lock timeout behavior, raw read/write errors, or configuration mismatches between participants.
