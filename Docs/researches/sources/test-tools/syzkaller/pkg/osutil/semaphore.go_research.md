# sources/test-tools/syzkaller/pkg/osutil/semaphore.go

Purpose: Implements a simple counting semaphore backed by a buffered channel.

Important APIs: `NewSemaphore`, `Wait`, `WaitC`, `Available`, and `Signal`.

Control flow and state: `NewSemaphore(count)` creates a channel of capacity `count` and fills it with `count` tokens. `Wait` receives one token. `WaitC` exposes the receive channel for select statements. `Available` returns current buffered token count. `Signal` sends a token back and panics if the semaphore already appears full.

Dependencies and integration: General utility for bounded concurrency in syzkaller packages.

Risks: `Available`/capacity check is not a synchronization guarantee under concurrent `Signal` calls, as the comment notes. Exposing `WaitC` allows callers to receive without paired signaling discipline.

Test signals: No direct tests in this shard.
