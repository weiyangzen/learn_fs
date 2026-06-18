# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/getopt.cpp

Wide-character, reentrant-style GNU getopt implementation for UDF command-line tools.

Key responsibilities:
- Implements `getopt_init()` to initialize caller-owned `optarg_ctx`.
- Maintains option ordering mode: require-order, permute, or return-nonoptions-in-order.
- Implements argument permutation through `exchange()` so options can be moved before non-options.
- Implements `_getopt_internal()` for short options, long options, optional/required arguments, abbreviation matching, ambiguity detection, `--` termination, and long-only fallback behavior.
- Exposes `getopt()` and `getopt_long()` wrappers over `_getopt_internal()`.

Important behavior:
- Uses wide-character string primitives via local macros (`wcschr`, `wcslen`, `wcsncmp`, `wcscmp`, and related names).
- `optind == 0` is the initialization signal; scanning starts at argv index 1.
- `optstring` prefix `-` selects return-in-order mode; prefix `+` selects require-order mode; otherwise the default is permutation.
- Long option abbreviation is accepted only if unique or exact.
- Returns `BAD_OPTION` for invalid/ambiguous options, `:` for missing required arguments only when requested by leading `:` in `optstring`, `1` for non-option values in return-in-order mode, and `EOF` at end.

Dependencies:
- Includes `getopt.h`.
- Uses `UDFPrint()` for diagnostics.
- Mutates `argv` order in permutation mode, matching GNU getopt behavior.

Notable risks:
- `ordering` is a file-static global, so the ordering mode is shared across contexts even though most scan state is per-`optarg_ctx`.
- `getopt_long_only()` is declared in the header but not implemented in this file.
- Error format strings mix wide and narrow specifiers in a few places, so diagnostics may be format-sensitive.
- The implementation assumes writable/permutable `argv` despite the prototype using `WCHAR *const *`.
