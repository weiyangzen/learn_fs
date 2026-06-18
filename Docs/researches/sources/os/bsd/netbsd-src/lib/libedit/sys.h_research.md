# File Research: sources/os/bsd/netbsd-src/lib/libedit/sys.h

## Purpose
Portability header for libedit. It centralizes compiler/system compatibility macros used by the rest of the libedit sources.

## Main Content
- Includes `<sys/cdefs.h>` when available.
- Provides fallback definitions for `__attribute__`, `__BEGIN_DECLS`, `__END_DECLS`, `__arraycount`, and `__RCSID`.
- Defines `libedit_private` as hidden symbol visibility.
- Selects POSIX.2 regex support via `REGEX` and explicitly disables old V8 `REGEXP`.

## Integration
Included through libedit internal headers to normalize NetBSD and non-NetBSD build environments.

## Risks / Notes
The visibility macro assumes compiler support for `__attribute__((visibility("hidden")))`; the header only suppresses `__attribute__` for older/non-GNU cases.
