# sources/user-network-fs/blobfuse2/common/exectime/runningstats.go
## sources/user-network-fs/blobfuse2/common/exectime/runningstats.go

Purpose: implements online running mean, variance, and standard deviation for duration samples.

Important APIs/types/functions: `RunningStatistics`, `NewRunningStatistics`, `Push`, `Mean`, `Variance`, and `StandardDeviation`.

Control flow: `Push` increments sample count. The first sample initializes old/new mean and zero variance accumulator. Subsequent samples apply Welford-style update formulas for mean and sum of squared deviations using `time.Duration` arithmetic. `Variance` returns sample variance (`N-1` denominator) for at least two samples, otherwise zero. `StandardDeviation` converts variance to float64, square-roots it, and converts back to duration.

State and persistence: stores only counters and duration accumulators in memory. No synchronization; callers must serialize access if shared across goroutines.

Dependencies/integration: used by `exectime.Timer.StatTimeCurrentBlock` and `PrintStats`.

Risks: duration multiplication/subtraction can overflow for very large durations or many samples. Converting a duration variance to float64 and back loses precision. No tests cover numerical behavior in this subset.

Test signals: indirect only through any manual use of `exectime`; no unit tests here.
