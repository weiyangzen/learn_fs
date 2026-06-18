# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/va_list.h

## Role

Defines internal variable-argument list types consumed by headers that need `va_list`-compatible declarations.

## Key Interfaces

- Defines `__va_alist_type` as `long` for LP64 and `int` otherwise.
- Defines `__va_void(expr)` and `__va_ptr_base`.
- For `__BUILTIN_VA_STRUCT` on amd64, defines `__va_list` as a one-element struct array with GP offset, FP offset, overflow area, and register save area pointer.
- For modern GCC, aliases `__gnuc_va_list` and `__va_list` to `__builtin_va_list`.
- Default fallback defines `__va_list` as `void *`.

## Design Notes

Applications are told not to include this directly; it exists so headers such as stdio, wchar, strlog, and syslog can mention va_list-related types safely.

## Risk Notes

The amd64 built-in structure fields must match compiler ABI expectations. The member name `__va_reg_sve_area` appears to be the register save area pointer used by this ABI definition.
