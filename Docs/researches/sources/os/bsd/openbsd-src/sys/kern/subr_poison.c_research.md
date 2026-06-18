# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_poison.c

## Role

Provides small memory poison helpers used to mark freed objects with recognizable values and later detect post-free modification.

## Key Behavior

- `poison_value()` derives one of four 32-bit poison patterns from the object’s page number, using configurable `DEADBEEF0`/`DEADBEEF1` defaults when provided.
- `poison_mem()` writes the selected poison value into the first 64 bytes, rounded down to whole 32-bit words.
- `poison_check()` verifies the same bounded region and reports the first mismatching word index and expected poison value.

## Interfaces And Dependencies

Uses `PAGE_SHIFT`, `uint32_t`, and basic kernel types from `sys/param.h`.

## Notes

Only the first 64 bytes are poisoned or checked. The address-derived pattern makes adjacent pages less likely to share identical poison text while keeping the operation cheap.
