# File Research: sources/os/bsd/freebsd-src/sys/sys/syslimits.h

## Scope

This header defines a small set of POSIX/system limit constants used by userland and the kernel-facing public headers. It intentionally avoids defining values that applications should obtain dynamically through `sysconf()`.

## APIs And Constants

- Defines `ARG_MAX` as `2 * 256 * 1024` except on `__ILP32__`, where it is `256 * 1024`.
- Defines defaults for `CHILD_MAX`, `NGROUPS_MAX`, and `OPEN_MAX` only when not already provided.
- Defines terminal, pathname, pipe, and vector limits: `MAX_CANON`, `MAX_INPUT`, `NAME_MAX`, `PATH_MAX`, `PIPE_BUF`, and `IOV_MAX`.
- Leaves `HOST_NAME_MAX` undefined by design.

## Control Flow And Integration

- This file is purely declarative and has no runtime control flow.
- It warns when included directly outside the intended include chain, unless building standalone, kernel, `<limits.h>`, or `<sys/param.h>` contexts.
- The comments explicitly discourage adding new variables here because many limits are runtime-configurable or should be queried dynamically.

## Dependencies

- No type dependencies beyond the preprocessor context.
- Consumed by public limits headers and kernel/userland code that needs legacy compile-time constants.

## Risks And Invariants

- Compile-time constants here are ABI and application-compatibility expectations; lowering values can break existing builds or runtime assumptions.
- Defining too many dynamic limits statically can encourage incorrect portable code, which is why `HOST_NAME_MAX` remains undefined.
- The ILP32 `ARG_MAX` split reflects kernel virtual-address-space pressure and should not be changed without checking exec argument-copy paths.
