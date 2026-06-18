# sources/sync-backup/rsync/lib/snprintf.c

Purpose: fallback implementation of `snprintf`, `vsnprintf`, `asprintf`, and `vasprintf` for platforms with missing or non-C99-compliant printf functions.

Important APIs/types/functions: conditional `rsync_vsnprintf`, `rsync_snprintf`, `vasprintf`, `asprintf`, parser/formatter `dopr`, `fmtstr`, `fmtint`, `fmtfp`, `dopr_outch`, `new_chunk`, and `add_cnk_list_entry`; structures `pr_chunk` and `pr_chunk_x`; parser state constants `DP_S_*`, flags `DP_F_*`, conversion flags `DP_C_*`, and chunk types `CNK_*`.

Control flow: when fallback is needed, `dopr` first parses the format string into chunks, including positional parameters and `*` width/precision references. It then walks the `va_list` in parameter order, verifies repeated positional references use the same type, stores values in chunks, and finally renders chunks into the output buffer while maintaining C99 return length semantics and null termination. `fmtstr`, `fmtint`, and `fmtfp` handle padding, precision, signs, integer bases, and simple fixed-point floating output. `vasprintf` performs a sizing `vsnprintf(NULL, 0, ...)`, allocates `ret + 1`, and renders again; `asprintf` wraps it with varargs.

State and persistence behavior: parsing chunks and positional lists are heap-allocated per call and freed before return. `asprintf`/`vasprintf` return heap memory owned by the caller. No global runtime state.

Dependencies/integration: driven by configure macros `HAVE_SNPRINTF`, `HAVE_VSNPRINTF`, `HAVE_C99_VSNPRINTF`, `HAVE_ASPRINTF`, and `HAVE_VASPRINTF`; included in rsync portability builds and mapped through macros in `rsync.h` when needed. Test mode can force fallback compilation and compare against system `sprintf`.

Risks/test signals: the fallback is broad but not a complete modern printf: hex float is not implemented, exponent/general formats are treated through fixed `fmtfp`, floating precision is capped at 9 decimals, and positional-parameter validation can reject formats some libcs accept. `%n` writes through caller pointers and must retain standard semantics. Tests should compile with `TEST_SNPRINTF`, compare return values and truncation behavior, cover positional width/precision, `%.*s` overread prevention, size_t/long long, NULL strings, `asprintf` allocation failure, and platforms with only partial libc support.
