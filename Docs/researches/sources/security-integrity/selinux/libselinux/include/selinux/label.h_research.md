# sources/security-integrity/selinux/libselinux/include/selinux/label.h

## Purpose
`label.h` declares the libselinux labeling interface used by userspace object managers and tools to load label backends and look up security contexts for files, media, X objects, databases, Android properties, and services.

## Important APIs, types, and functions
The central opaque type is `struct selabel_handle`. Backend constants include `SELABEL_CTX_FILE`, `MEDIA`, `X`, `DB`, `ANDROID_PROP`, and `ANDROID_SERVICE`. Options include validation, base-only loading, alternate path, subset, and digest. APIs include `selabel_open()`, `selabel_close()`, `selabel_lookup()`, `selabel_lookup_raw()`, partial-match and digest/hash helpers, best-match lookups, `selabel_digest()`, `selabel_cmp()`, and `selabel_stats()`. It also defines X and DB type codes and `enum selabel_cmp_result`.

## Control flow
Callers open a backend with optional `struct selinux_opt` values, perform one or more lookups using backend-specific keys and type codes, optionally inspect digests/statistics or compare handles, and close the handle. Raw variants bypass translation where applicable.

## State and persistence behavior
Each handle owns parsed label configuration and any backend-specific caches or digests. The API reads policy context files but does not modify them. Returned contexts are caller-owned and freed with `freecon()`, while digest/specfile pointers follow implementation-defined ownership documented by the man page.

## Dependencies and integration points
The header depends on `selinux/selinux.h`, `stdbool.h`, `stdint.h`, and `sys/types.h`. It integrates with restorecon, matchpathcon replacement paths, file-context validation, Android labeling backends, and tools needing digest comparison against `security.sehash`.

## Risks and edge cases
Backend/type combinations are not universally valid. Callers must not use handles after `selabel_close()`. Digest APIs require `SELABEL_OPT_DIGEST`; otherwise callers can receive failures or missing data. Raw versus translated context use must match the caller's audit/display needs. Partial and best-match behavior can be subtle for aliases and file modes.

## Test signals
Tests should cover each backend where available, option parsing, file lookup by path/mode, raw and translated lookups, aliases in best-match calls, digest generation and specfile lists, handle comparison outcomes, partial-match queries, invalid backend/options, and close-after-use safety.
