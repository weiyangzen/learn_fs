# sources/sync-backup/syncthing/lib/connections/limiter.go

## sources/sync-backup/syncthing/lib/connections/limiter.go

Purpose: Applies global and per-device read/write bandwidth rate limits to connection streams and updates them on config changes.

Important APIs/types/functions: `limiter` implements `config.Committer`; `newLimiter`, `setLimitsLocked`, `processDevicesConfigurationLocked`, `CommitConfiguration`, `getLimiters`, `newLimitedReaderLocked`, `newLimitedWriterLocked`, per-device limiter accessors, `limitedReader`, `limitedWriter`, `waiterHolder`, and `totalWaiter`.

Control flow and state: Construction subscribes to the config wrapper and initializes global/per-device rate limiters. On config commit, it updates per-device limiters, removes deleted-device limiters, updates global send/recv limiters, and stores whether LAN should be limited. `getLimiters` wraps an `io.ReadWriter` with readers/writers that wait on both per-device and global token buckets. Reads consume after reading; writes split large buffers into adaptive chunks to avoid bursty writes and avoid `WaitN` calls larger than the burst size.

Dependencies and integration: Uses `golang.org/x/time/rate`, `config.Wrapper`, `protocol.DeviceID`, `io`, atomics, locks, and logging. Called by connection setup to wrap streams after LAN classification.

Risks and test signals: Correct lock scope matters because config commits and stream creation can race. Token waits use `context.TODO`, so a blocked limiter wait is not cancelable. LAN exemption depends on `LimitBandwidthInLan`. No direct limiter tests in this subset, but config bandwidth tests and connection tests exercise surrounding behavior.
