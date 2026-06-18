# sources/object-store/openstack-swift/doc/saio/swift/object-expirer.conf

## Purpose
SAIO object-expirer daemon config. It scans expiration queues and deletes expired objects through a proxy pipeline.

## Important Sections
Defaults set placeholder user, `log_name = object-expirer`, `LOG_LOCAL6`, and info logging. `[object-expirer]` sets `interval = 300` and documents concurrency/process partition settings. Pipeline is `catch_errors cache proxy-server`.

## Control Flow and Integration
The expirer wakes every 300 seconds, reads queue objects, and uses the configured proxy app with cache and catch-errors middleware to issue deletes. Process options can partition work when run with multiple workers.

## State, Risks, and Test Signals
Expiration queue state is stored in Swift objects/containers, not in this file. Risks are low visibility if logging is misconfigured and accidental single-process bottleneck if concurrency/process settings remain defaults. Test signal is expiration queue processing and successful deletes through the proxy.
