# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/linker_set.h

## Role

FreeBSD-derived linker-set helper macros for collecting pointers into named ELF sections and iterating them through weak start/stop symbols.

## Structure

Defines concatenation/stringification helpers, weak/global assembly symbol helpers, `__MAKE_SET()`, public set-entry macros (`TEXT_SET`, `DATA_SET`, `BSS_SET`, `ABS_SET`, `SET_ENTRY`), declaration and begin/limit macros, iteration, indexing, and count helpers.

## Dependencies And Consumers

Includes `sys/ccompile.h` for compiler attributes such as `__section`, `__used`, and `__weak_symbol`. Consumers register pointers into `set_<name>` sections and later walk `__start_set_<name>` to `__stop_set_<name>`.

## Important Details

Set entries are addresses of symbols, so iterator variables are pointer-to-pointer style. Start and stop symbols are weak so an empty set can link, but consumers must still account for platform/linker behavior.

## Research Notes

Read completely: 99 lines, 3535 bytes.
