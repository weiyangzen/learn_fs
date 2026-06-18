# File Research: sources/windows/reactos/drivers/filesystems/udfs/sys_spec.h

## Purpose

`sys_spec.h` is the public include wrapper for UDFS system-specific support declarations.

## Main Contents

- Uses `_UDF_SYS_SPEC_H_` include guards.
- Includes `Include/Sys_spec_lib.h`.

## Integration

Other UDFS files include this header when they need the system-specific declarations supplied by the shared library header.

## Notable Details

The file contains no declarations of its own; it only wraps the shared system-specific header.
