# File Research: sources/os/bsd/openbsd-src/sys/sys/cdefs.h

This header provides foundational compiler, linkage, attribute, prediction, and standards-visibility macros used throughout OpenBSD headers.

Key definitions:
- Compiler/version helpers: `__GNUC_PREREQ__`, `__P`, `__CONCAT`, `__STRING`.
- Attribute wrappers: `__dead`, `__pure`, `__unused`, `__used`, `__warn_unused_result`, `__bounded`, `__returns_twice`, `__packed`, `__aligned`, `__malloc`.
- Inline/linkage helpers: `__only_inline`, `__BEGIN_EXTERN_C`, `__END_EXTERN_C`, visibility push/pop macros, and public/hidden declaration wrappers.
- Branch prediction: `__predict_true()` and `__predict_false()`.
- Feature exposure macros: `__POSIX_VISIBLE`, `__XPG_VISIBLE`, `__ISO_C_VISIBLE`, and `__BSD_VISIBLE`.

Behavior and integration:
- Includes `<machine/cdefs.h>` for machine-level additions.
- Normalizes `_XOPEN_SOURCE`, `_POSIX_C_SOURCE`, `_ANSI_SOURCE`, `_ISOC99_SOURCE`, `_ISOC11_SOURCE`, `__STDC_VERSION__`, and C++ levels into internal visibility values.
- Defaults to POSIX.1-2024, XPG 800, ISO C 2017, and BSD-visible interfaces when no restrictive feature-test macros are supplied.

Risk notes:
- This is a high-impact compatibility header; small changes can alter API exposure across the whole tree.
- Feature-test macro ordering is deliberate: X/Open settings can redefine `_POSIX_C_SOURCE`, and ISO/C++ settings can override ISO C visibility.
