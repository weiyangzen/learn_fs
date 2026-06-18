# File Research: sources/os/bsd/freebsd-src/sys/kern/clock_if.m

## Summary
Defines the KObj `clock` interface for device-independent clock drivers.

## Key Methods
- `gettime(device_t dev, struct timespec *ts)` reads the clock.
- `settime(device_t dev, struct timespec *ts)` sets the clock.

## Important Behavior
The comments specify that `EINVAL` from `gettime` means the clock has an illegal setting.

## Risks
This is an interface definition. Runtime behavior depends on driver implementations honoring the timespec contract and using `EINVAL` consistently for invalid hardware clock state.
