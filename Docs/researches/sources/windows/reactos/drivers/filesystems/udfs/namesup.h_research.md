# File Research: sources/windows/reactos/drivers/filesystems/udfs/namesup.h

## Role

`namesup.h` declares the UDF filename support API implemented by `namesup.cpp`.

## Interface

It exposes helpers for component dissection, wildcard expression matching, wildcard detection, name validity checks with stream-open reporting, match-all-mask detection, and 8.3-name eligibility.

## Dependencies

The declarations depend on UDF driver types such as `PVCB`, Windows `UNICODE_STRING`, and the DOS/open reporting conventions used by directory lookup and create paths.

## Notable Risks

The prototypes use `__fastcall` on selected helpers, so callers and definitions must agree on calling convention.
