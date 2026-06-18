# sources/user-network-fs/blobfuse2/common/exectime/exectime.go
## sources/user-network-fs/blobfuse2/common/exectime/exectime.go

Purpose: provides lightweight execution-time instrumentation with a package-level default timer.

Important APIs/types/functions: `Timer`, global `timer`, package functions `StatTimeCurrentBlock`, `PrintStats`, `TimeCurrentBlock`, `SwitchOnDebug`, `SwitchOffDebug`, `Start`, `Stop`, `New`, and `SetDefault`, plus matching methods on `Timer`.

Control flow: `TimeCurrentBlock` and `StatTimeCurrentBlock` return defer-friendly closures. When debug is enabled, the closure records elapsed time or pushes it into a `RunningStatistics` bucket; when disabled, it is a no-op. `PrintStats` writes a separator and per-key average/stddev/total/ops-per-sec. `Start` stores `time.Now()` by key and `Stop` writes elapsed time since that key. `init` defaults to stdout with debug enabled.

State and persistence: global mutable timer contains writer, debug flag, `timeMap`, and `statsMap`. No locking is used around maps, so concurrent instrumentation can race. Output is written to the configured writer but not otherwise persisted by this package.

Dependencies/integration: uses `RunningStatistics`, `io.Writer`, stdout, and `time`.

Risks: debug defaults to true, so instrumentation may write unexpectedly unless disabled. `Stop` on an unknown key uses zero `time.Time`, producing a huge duration. `PrintStats` divides by mean seconds; a zero-duration mean can create invalid rates. Maps are not concurrency-safe.

Test signals: no dedicated tests in this subset; behavior is simple but concurrency and unknown-key cases are untested.
