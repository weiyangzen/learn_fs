# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/wprintf-parse.h

Purpose: defines wide-character printf directive metadata and parser API.

Important APIs/types/functions: it duplicates the narrow parser contract using `wchar_t` pointers and conversion fields. `wchar_t_directive` records directive, width, precision, argument indices, flags, and conversion. `wchar_t_directives` holds the directive array and max width/precision lengths. It declares `wprintf_parse`.

State and persistence: no state. Parsed directive pointers refer into the original wide format string and must not outlive it.

Dependencies and integration: includes `printf-args.h`; implemented by compiling `printf-parse.c` with `WIDE_CHAR_VERSION`. Used by wide `vasnprintf.c` and `printf.c` fallback wrappers.

Risks and test signals: duplicated constants must remain compatible with narrow parsing, and wide conversion aliases must match platform support. Test positional wide formats, width/precision `*`, `%lc`/`%ls`, `C`/`S`, and memory cleanup on parse errors.
