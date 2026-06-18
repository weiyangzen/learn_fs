# File Research: sources/os/bsd/dragonflybsd/sys/kern/device_if.m

## Summary
Defines the DragonFly BSD `device` kernel object interface used by generated driver method glue. It covers standard probe, identify, attach, detach, shutdown, suspend, resume, quiesce, and register hooks.

## Main Responsibilities
- Declares the core device lifecycle method set.
- Documents probe return-value semantics, including negative priority matches and positive errno failures.
- Provides null defaults for shutdown, suspend, resume, quiesce, and register.

## Key Methods
- `probe(device_t dev)`.
- Static `identify(driver_t *driver, device_t parent)`.
- `attach(device_t dev)`.
- `detach(device_t dev)`.
- `shutdown`, `suspend`, `resume`, `quiesce`, `register`.

## Important Behavior
A probe success code below zero is only a priority match; drivers returning it must not assume attach will follow or that probe-time softc state survives. A zero probe success means the driver can assume it will attach.

## Risks
This is a cross-driver ABI surface. Incorrect default assumptions in drivers can leak probe resources or retain invalid softc state when competing drivers probe the same device.
