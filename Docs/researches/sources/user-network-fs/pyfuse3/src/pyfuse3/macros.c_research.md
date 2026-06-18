# sources/user-network-fs/pyfuse3/src/pyfuse3/macros.c

Purpose: Defines platform-specific preprocessor macros for accessing nanosecond fields in `struct stat` and assigning Darwin-only or non-Darwin fields.

Important APIs/types/functions: Linux macros access `st_atim`, `st_ctim`, and `st_mtim`; BSD/Darwin macros access `st_atimespec`, `st_ctimespec`, `st_mtimespec`, and birthtime fields. `ASSIGN_DARWIN` and `ASSIGN_NOT_DARWIN` conditionally assign fields by platform.

Control flow: Compile-time `#if PLATFORM` branches select the correct struct layout. Unknown platforms fail compilation.

State and persistence: No runtime state; this is compile-time portability glue.

Dependencies and integration points: Included by native pyfuse3/Cython code that maps system stat data into Python-facing attributes.

Risks: The file uses `.c` extension despite containing macro definitions; it must be included, not independently compiled as a normal translation unit without context. Incorrect platform detection would produce invalid struct-field access.

Test signals: `test_rounding.py`, `test_api.py::test_entry_res`, and example filesystem timestamp checks are indirect signals for timestamp precision and conversion.
