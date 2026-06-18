# sources/test-tools/strace/bundled/linux/include/uapi/linux/stddef.h

## Purpose

Provides UAPI helper macros for inline annotation, mirrored struct groups, flexible arrays inside unions, counted-by annotations, and nonstring markers. This supports source compatibility for many other UAPI headers and for userspace builds of strace's bundled headers.

## Important APIs, Types, and Dependencies

There are no include dependencies. Exports include fallback `__always_inline`, `__struct_group_tag`, `__struct_group(TAG, NAME, ATTRS, MEMBERS...)`, C++ and C-specific `__DECLARE_FLEX_ARRAY`, no-op `__counted_by`, `__counted_by_le`, `__counted_by_be`, and `__kernel_nonstring`.

## Control Flow, State, and Integration

The header is macro-only. The control effect is compile-time: it preserves layout by creating anonymous and named struct views over identical members, and it permits flexible-array-like declarations in contexts that standard C otherwise rejects. It has no runtime or persistence behavior.

## Risks and Test Signals

Risks include C/C++ layout differences, compiler extension assumptions around anonymous structs/unions, and losing counted-by annotations when consumers expect them for static analysis. Test signals are successful compilation of headers that use these macros, structure offset checks, and no runtime strace behavior changes.
