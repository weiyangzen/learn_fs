# sources/test-tools/fio/lib/nowarn_snprintf.h

Purpose: wraps `vsnprintf` while locally suppressing GCC 8+ `-Wformat-truncation` diagnostics.

Important APIs/functions: inline `nowarn_snprintf(char *str, size_t size, const char *format, ...)`.

Control flow/state: starts a `va_list`, pushes diagnostic state for GCC >= 8, calls `vsnprintf`, restores diagnostics, ends the varargs, and returns the `vsnprintf` result.

Dependencies/integration: includes `stdio.h` and `stdarg.h`. Used where truncation is intentional or externally bounded and the normal warning would be noisy.

Risks/test signals: suppressing warnings can hide real truncation bugs, so use should be narrow. Tests should verify return values match `snprintf` and that truncation behavior is still caller-checked where correctness matters.
