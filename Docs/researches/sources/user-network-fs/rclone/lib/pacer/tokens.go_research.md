# sources/user-network-fs/rclone/lib/pacer/tokens.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pacer/tokens.go -->
## sources/user-network-fs/rclone/lib/pacer/tokens.go

Purpose: provides a minimal token dispenser for bounding concurrency. It is intentionally smaller than a full semaphore wrapper and exposes blocking `Get`/`Put` operations over a buffered channel.

Important APIs and control flow: `TokenDispenser` owns `tokens chan struct{}`. `NewTokenDispenser(n)` constructs a channel with capacity `n` and pre-fills it with `n` tokens. `Get()` receives from the channel and blocks when no token is available. `Put()` sends a token back and blocks if the channel is already full.

State, dependencies, and integration: all state is the channel occupancy. There are no external package dependencies. The type integrates wherever rclone needs simple fixed-width admission control, especially code paths that prefer blocking semantics over context-aware acquisition.

Risks and test signals: `Put` can deadlock if called more often than `Get`; `Get` can block forever if tokens are leaked; there is no context cancellation. `NewTokenDispenser(0)` creates a permanently blocking dispenser. The paired test verifies initial fill and channel length changes for a normal size.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pacer/tokens.go -->
