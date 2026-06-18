# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/dadev.h

## Scope

Complete file read, 41 lines. This is an umbrella include header for DKTP direct-access device code.

## Public Surface

It includes:

- `sys/dktp/controller.h`
- `sys/dktp/cmpkt.h`
- `sys/dktp/gda.h`

It declares no new structures, macros, functions, or constants.

## Behavior And Integration

This header groups the controller, command-packet, and generic disk adapter interfaces under one include for older direct-access disk code.

## Dependencies And Invariants

All meaningful API surface is inherited from the included DKTP headers.

## Risks

Because it re-exports several DKTP headers transitively, including it can hide direct dependencies and increase compile coupling.
