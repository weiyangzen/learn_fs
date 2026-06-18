# File Research: sources/os/bsd/freebsd-src/sys/kern/device_if.m

## Summary
Defines the KObj `device` interface implemented by all FreeBSD device drivers. It covers driver matching, child identification, attach/detach, shutdown, suspend/resume, quiesce, and handler registration.

## Key Methods
- `probe(device_t dev)` participates in driver election. Return `0` wins immediately, negative values are ranked matches, `ENXIO` means no match, and positive errno values signal errors.
- `identify(driver_t *driver, device_t parent)` lets drivers enumerate children not otherwise discovered.
- `attach(device_t dev)` initializes hardware and allocates resources after a successful probe.
- `detach(device_t dev)` tears down a driver instance.
- `shutdown`, `suspend`, `resume`, `quiesce`, and `register` handle system-wide lifecycle and registration events.

## Defaults and Instrumentation
Default no-op implementations exist for shutdown, suspend, resume, quiesce, and register. Probe and attach methods include `TSENTER2`/`TSEXIT2` timestamp instrumentation around `device_get_name(dev)`.

## Integration
Generated wrappers from this `.m` file are used throughout kernel autoconfiguration and driver lifecycle code. Documentation comments describe normal `KOBJMETHOD(device_*, ...)` usage.

## Risks
Probe return semantics are subtle and affect which driver attaches. Drivers must release probe-time resources before returning because a successful probe does not guarantee attachment unless it returns the special immediate-match value.
