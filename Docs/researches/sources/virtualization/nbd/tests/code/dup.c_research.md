# File Research: sources/virtualization/nbd/tests/code/dup.c

## Purpose
Tests that `dup_serve()` creates a distinct `SERVER` copy while preserving configured field values.

## Main Entry Points
- `stringcmp()` compares possibly NULL strings.
- `main()` constructs a populated `SERVER`, duplicates it, and uses `count_assert()` on each important field.

## Dependencies
Includes `nbdsrv.h` and `macro.h`.

## Risks and Notes
The test checks equality of values but does not verify that every duplicated string has distinct storage.
