# File Research: sources/os/bsd/dragonflybsd/sys/sys/cpputil.h

Preprocessor utility header for variadic macro metaprogramming.

Key responsibilities:
- Defines `VA_NARGS(...)` to count variadic arguments up to 64, with the documented caveat that empty args count as 1.
- Defines `__GENSTRUCT(tag, args...)`, dispatching to numbered macros that emit a `struct tag` with each argument as a field declaration.
- Provides `__GENSTRUCT1` through `__GENSTRUCT19`.

Dependencies:
- Includes `sys/cdefs.h` for `__CONCAT`.

Notable risks:
- The argument counter supports more arguments than the generated struct macros implement; calls above 19 fields will dispatch to undefined macros.
- This intentionally abuses preprocessor behavior and should be used only where existing local patterns require it.
