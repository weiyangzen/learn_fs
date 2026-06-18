# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lombus.h

## Role

LOMbus child-driver interface definitions for register spaces, register specs, internally generated error codes, and timing constants.

## Structure

Defines `lombus_regspec_t` triples, register space IDs for virtual registers, watchdog pat, and async event info, register ranges and special negative fault/probe/async registers, `enum lombus_errs`, and nanosecond timeout/pat constants.

## Dependencies And Consumers

No includes beyond C wrapper. Consumed by LOMbus parent/child drivers to interpret regspecs and fault conditions.

## Important Details

Error codes start at `0x100` to avoid LOM-generated `0x00-0x7f` and SunVTS `0x80-0xff` ranges. Time constants are `long long` nanoseconds.

## Research Notes

Read completely: 125 lines, 3275 bytes.
