# `sources/test-tools/filebench/utils.h`

Purpose: Declares Filebench utility functions and maps `fb_strlcpy`/`fb_strlcat` to native platform functions when available.

Important APIs: `fb_stralloc()`, `fb_strlcat()`, `fb_strlcpy()`, `fb_set_shmmax()`, and `fb_set_rlimit()`. The `HAVE_STRLCAT` and `HAVE_STRLCPY` branches define macros to native `strlcat`/`strlcpy`; otherwise external fallback functions are declared.

Control flow and integration: Included by parser, variable, and runtime modules needing portable string copying or startup resource tuning. It is a thin declaration layer over `utils.c`.

State and persistence: No state is declared here, but the resource-limit functions can mutate process or kernel state when implemented.

Dependencies: Includes `filebench.h` for Filebench common types and configure-derived declarations.

Risks and test signals: Macro substitution means callers may see either native or fallback semantics depending on configure results. Tests should build on platforms with and without native `strl*` functions and confirm prototypes match system headers.
