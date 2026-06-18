# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_stats.py

## Purpose
This module tests `allmydata.stats.CPUUsageMonitor`, specifically that it starts as a Twisted service, collects enough samples, trims its history, and begins exposing expected CPU usage metrics.

## Important APIs, Types, And Functions
`FasterMonitor` subclasses `CPUUsageMonitor` and lowers `POLL_INTERVAL` to `0.01` seconds for test speed. `CPUUsage` combines Twisted Trial, `pollmixin.PollMixin`, and `StallMixin`. `setUp` starts a `service.MultiService`, `tearDown` stops it, and `test_monitor` drives the monitor lifecycle.

## Control Flow
The test first calls `get_stats()` before the monitor has a service parent and verifies the rolling average key is absent. It then attaches the monitor with `setServiceParent(self.s)`, polls until `len(m.samples) == m.HISTORY_LENGTH + 1`, stalls for two more fast polling intervals to exercise history trimming, and finally checks that `get_stats()` includes `cpu_monitor.1min_avg`, `cpu_monitor.5min_avg`, `cpu_monitor.15min_avg`, and `cpu_monitor.total`.

## State And Persistence Behavior
The monitor keeps in-memory CPU samples while running as a Twisted service. The test intentionally waits for one more sample than `HISTORY_LENGTH` and then stalls again so trimming code is covered. No filesystem or external persistent state is used.

## Dependencies And Integration Points
The module depends on Twisted Trial, `twisted.application.service.MultiService`, Tahoe's `CPUUsageMonitor`, `pollmixin`, and `StallMixin`. It verifies that the stats monitor integrates with Twisted's service-parent lifecycle and exposes keys expected by Tahoe's stats collection/reporting layer.

## Risks And Edge Cases
The test is timing-sensitive because it depends on periodic polling. `FasterMonitor` reduces runtime but still relies on reactor scheduling and CPU sampling availability. It checks key presence rather than numeric values, so it catches lifecycle and publication regressions but not detailed CPU calculation errors.

## Test Signals
Passing tests signal that CPU monitoring is quiet before startup, begins collecting after service attachment, maintains/trims sample history, and publishes the expected rolling and total CPU stat keys.
