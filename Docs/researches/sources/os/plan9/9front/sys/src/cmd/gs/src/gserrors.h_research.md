# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gserrors.h

This header defines library error codes as negative integer constants.

The comments state the convention: procedures that may fail return nonnegative success values and negative failures. Integers are used instead of enums to avoid casting.

Defined errors include:
- General unknown/fatal/interrupt.
- Access/file/font/io/limit/range/type/undefined errors.
- VM and unregistered errors.
- `gs_error_hit_detected` as a special hit-detection signal.
- `gs_error_Fatal`.

These codes are used across all implementation files in this group.
