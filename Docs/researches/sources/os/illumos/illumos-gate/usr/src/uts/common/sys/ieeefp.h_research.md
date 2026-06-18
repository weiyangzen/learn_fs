# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ieeefp.h

This header defines Sun/illumos IEEE floating-point enums for rounding, precision, exceptions, trap bits, and FP classes.

Architecture-specific definitions:
- On SPARC:
  - `fp_direction_type`: nearest, tozero, positive, negative.
  - `fp_precision_type`: extended, single, double, precision_3.
  - `fp_exception_type`: inexact, division, underflow, overflow, invalid.
  - `N_IEEE_EXCEPTION` is 5.
  - Trap enum mirrors those five exceptions.
- On i386/amd64:
  - Direction values differ: nearest, negative, positive, tozero.
  - Precision values differ: single, precision_3, double, extended.
  - Exception enum includes denormalized and has 6 entries.
  - `N_IEEE_EXCEPTION` is 6.

Common definition:
- `fp_class_type`: zero, subnormal, normal, infinity, quiet, signaling.

Relevance:
- General ABI/standards header; not directly storage-related.
- Can affect kernel/user ABI compatibility for floating-point state consumers.
