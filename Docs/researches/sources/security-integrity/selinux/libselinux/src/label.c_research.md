# sources/security-integrity/selinux/libselinux/src/label.c

Purpose: Implements the frontend for SELinux labeling backends. It opens backend handles, validates/translates lookup records lazily, exposes lookup, best-match, digest, compare, stats, and close APIs.

Important APIs/types/functions: public functions include `selabel_open()`, `selabel_lookup[_raw]()`, `selabel_lookup_best_match[_raw]()`, `selabel_partial_match()`, digest helpers, `selabel_cmp()`, `selabel_close()`, and `selabel_stats()`. Internal `selabel_handle` function pointers are defined in `label_internal.h`.

Control flow: `selabel_open()` validates backend ID and compiled backend availability, allocates a handle, records validation/digest options, and calls the backend init function. Lookup APIs call backend-specific lookup, then `selabel_fini()` validates raw contexts and optionally lazily translates them under per-record lock with atomics. Digest setup allocates SHA1 storage and specfile list when requested.

State and persistence: each handle owns backend data, spec file path, and optional digest state. Lookup records cache validation and translated context strings until close.

Dependencies and integration: dispatches to file, media, X, DB, Android property/service backends depending on compile flags. Uses global validation callback and raw/trans context conversion.

Risks and test signals: lazy validation/translation must be thread-safe. Tests should cover unsupported backends, disabled backend `ENOTSUP`, digest option, raw vs translated lookups, lookup best match, compare incompatible handles, and close cleanup.
