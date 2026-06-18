# File Research: sources/virtualization/libguestfs/lib/guestfs-internal-all.h

Purpose: Shared internal header for all libguestfs C components, including daemon, library, bindings, and tools.

Key contents:
- Defines compiler compatibility macros, string comparison/prefix/suffix helpers, `ADD_ARG`, `MAX/MIN`, socket compatibility constants, and Apple XDR compatibility.
- Provides `is_zero`, an inline buffer-zero test optimized by checking the first 16 bytes then using `memcmp`.
- Defines `COMPILE_REGEXP`, a constructor/destructor macro for compiling PCRE2 regexes at library load time.
- Defines shared `mountable_type_t` for parsed mountables.
- Declares gnulib replacement prototypes for `accept4` and `pipe2` when needed.
- Provides OCaml compatibility alias for older OCaml runtime naming.

Dependencies and state:
- Uses libc string APIs, PCRE2, and low-level `write` in regexp compile failure handling.
- No runtime state except static regex objects created by `COMPILE_REGEXP` users.

Risks:
- Convenience macros evaluate some arguments multiple times, so callers must avoid side-effect expressions.
- `ADD_ARG` aborts on overflow rather than returning an error.
