# sources/security-integrity/cryfs/crates/cryfs-runner/src/ipc/pipe.rs

## Purpose
Provides length-prefixed, postcard-encoded unnamed-pipe IPC primitives with CLOEXEC setup, bounded message size, raw handshake support, and timeout reads.

## Important APIs, types, and functions
- `pipe<T>` creates a typed `Sender<T>`/`Receiver<T>` pair and sets `FD_CLOEXEC` on both ends.
- `Sender::send`, `send_raw`, and `write_length_prefixed` serialize or send raw bytes with a 1 MiB cap.
- `Receiver::recv`, `recv_timeout`, and `recv_raw_timeout` read length-prefixed payloads, optionally with nonblocking timeout.
- `read_exact_with_timeout` uses `poll` to avoid busy-waiting.

## Control flow
Pipe creation panics if a tokio runtime is already active, enforcing single-threaded creation to reduce fork/CLOEXEC races on platforms without atomic `pipe2(O_CLOEXEC)`. Sending writes a little-endian u32 length and payload. Timeout receive sets nonblocking mode, reads the length and payload before a deadline, and reports EOF, timeout, oversize, poll, or decode errors.

## State and persistence behavior
Only OS pipe descriptors and transient serialized bytes are managed. `into_owned_fd` and `from_owned_fd` transfer fd ownership across spawn boundaries.

## Dependencies and integration points
Depends on `interprocess` unnamed pipes, `postcard`, serde, `nix::poll`, `libc` fcntl, and tokio runtime detection. `rpc.rs` builds typed request/response channels on top of it; `spawn.rs` maps descriptors into daemon children.

## Risks and edge cases
CLOEXEC is set after pipe creation, so a narrow race remains if another thread forks before fcntl; the runtime guard is a usage invariant, not a kernel guarantee. Timeout conversion caps poll waits at `u16::MAX` ms per poll. Typed and raw receive share the same wire framing, so ordering must be respected by handshake code.

## Test signals
In-file tests cover CLOEXEC flags, dropped endpoints, blocking receive, timeout receive, zero/short/large/multiple messages, partial length/payload EOF, raw payload round trips, max-size rejection, little-endian framing, and typed-vs-raw byte behavior.
