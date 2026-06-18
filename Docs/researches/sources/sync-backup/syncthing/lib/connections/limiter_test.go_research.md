## sources/sync-backup/syncthing/lib/connections/limiter_test.go

Purpose: Tests the connection bandwidth limiter behavior around per-device receive/send limits, dynamic config updates, LAN bypass behavior, and aggregate waiter limit selection.

Important APIs/types/functions: `initConfig` constructs a `config.Wrapper` with four devices and starts its service loop; `newDeviceConfiguration` creates device configs from wrapper defaults; tests exercise `newLimiter`, limiter internal maps, `limitedWriter.Write`, `totalWaiter.Limit`, and helper `checkActualAndExpected`. `countingWriter` measures write fragmentation.

Control flow: The tests initialize fixed `protocol.DeviceID` values, mutate device `MaxRecvKbps` and `MaxSendKbps`, wait for config change propagation, then compare limiter maps against expected `rate.Limiter` limits. Writer tests copy random bytes through `limitedWriter` in limited, LAN-bypassed, fully-unlimited, and mixed-limiter modes to verify chunking and fast paths.

State and persistence: State is in-memory test config, limiter maps, and atomic LAN-limit flags. No filesystem persistence is involved beyond using `/dev/null` as config path.

Dependencies and integration points: Uses `config.Wrapper` subscription delivery, `events.NoopLogger`, `protocol.DeviceID`, and `golang.org/x/time/rate`. It indirectly validates assumptions used by `service.handleHellos`, which wraps accepted connections with limiter readers/writers.

Risks: Random rate values can make failures harder to reproduce, though assertions compare only limits and write-count ranges. The tests inspect unexported limiter internals, so internal refactors need test updates.

Test signals: Strong coverage for limiter initialization, add/remove/update propagation, writer fast path, LAN exemption, and combined waiter minimum-rate semantics.
