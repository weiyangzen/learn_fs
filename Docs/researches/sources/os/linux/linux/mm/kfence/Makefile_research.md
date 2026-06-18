# File Research: sources/os/linux/linux/mm/kfence/Makefile

## Role

Build rules for the KFENCE subsystem.

## Contents

- Enables `CONTEXT_ANALYSIS := y`.
- Always builds `core.o` and `report.o` into the KFENCE object set.
- Builds `kfence_test.o` when `CONFIG_KFENCE_KUNIT_TEST` is enabled.
- Applies `-fno-omit-frame-pointer` and `-fno-optimize-sibling-calls` to `kfence_test.o` for reliable test stack traces.

## Research Notes

The Makefile keeps production KFENCE split between allocation/fault core logic and reporting, with KUnit tests compiled only under the test config.
