# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/udf_lib_common.h

## Purpose
Defines a small user/library status and callback interface for UDF library operations.

## Main Contents
- Includes `udferr_usr.h` unless `WITHOUT_FORMATTER` is set.
- Defines `UDF_STATUS` as `LONG` and `UDF_SUCCESS(x)` as non-negative status.
- Defines callback signatures for read, write, ioctl, reopen, get-size, and flush operations.

## Architectural Role
This is a thin abstraction layer for user-mode formatter/library code to operate over a caller-provided device/image backend.
