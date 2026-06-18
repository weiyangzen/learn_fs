# Research: sources/object-store/minio-mc/cmd/pipechan.go

## sources/object-store/minio-mc/cmd/pipechan.go

Purpose: provides `PipeChan`, a dynamically resizing logical channel for filesystem notification events, intended to reduce sender blocking when event bursts exceed a fixed channel capacity.

Important APIs and functions: `PipeChan(capacity int) (inputCh, outputCh chan notify.EventInfo)` is the only exported API in this file. It returns an input channel for producers and an output channel for consumers.

Control flow: one goroutine reads from `inputCh`, creates internal channels, and switches to larger or smaller internal channels based on current length thresholds. A second goroutine drains each internal channel in sequence into `outputCh`, then closes output when all internal channels close.

State and persistence: in-memory channels only. It may allocate increasingly large buffers during bursts.

Dependencies and integration: works with `github.com/rjeczalik/notify.EventInfo`, likely used by watch code outside this subset.

Risks and tests: `capacity <= 0` would create zero-capacity channels and can make threshold logic problematic. The shrink condition checks `len(currCh) >= capacity && len(currCh) <= cap(currCh)/4`, which is hard to reach after the growth condition and may not shrink as intended. Covered by `pipechan_test.go`.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pipechan.go -->
