# File Research: sources/virtualization/guestfs-tools/gnulib/lib/ignore-value.h

Macro helper for intentionally ignoring return values from functions annotated with `warn_unused_result`.

Behavior:
- For affected GCC versions, stores expression result in a temporary via `__typeof__` and discards it.
- For clang and other compilers, falls back to `(void)(x)`.

Research relevance: portability/helper macro for explicit unchecked-result cases.
