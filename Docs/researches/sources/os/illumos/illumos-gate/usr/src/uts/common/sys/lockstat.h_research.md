# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lockstat.h

## Role

DTrace lockstat probe ID/name definitions and kernel macros for recording lock acquisition, release, spin, block, upgrade, and downgrade events.

## Structure

Defines 25 probe IDs, string names for lock operations/events/types, composed provider names, and under non-assembly kernel builds declares `lockstat_probemap`, `lockstat_probe`, and support functions. Provides `LOCKSTAT_RECORD*`, `LOCKSTAT_START_TIME`, and `LOCKSTAT_RECORD_TIME` macros.

## Dependencies And Consumers

Includes `sys/dtrace.h`, and in C builds includes types, inttypes, systm, and atomic headers. Consumers are synchronization primitives and lockstat/DTrace support code.

## Important Details

The record macros guard on `lockstat_probemap[probe]`, increment `curthread->t_lockstat`, use `membar_enter()`, re-read the probe ID, then call the DTrace probe. On ILP32, elapsed spin time is clamped to `UINT_MAX`.

## Research Notes

Read completely: 192 lines, 5707 bytes.
