# File Research: sources/os/bsd/netbsd-src/lib/libc/time/private.h

## Purpose
Private portability and configuration header for NetBSD’s tzcode-derived time implementation. It defines feature defaults, compiler/library compatibility shims, exported/private time API declarations, integer/time bounds helpers, attributes, gettext support, and calendar constants used by `localtime.c`, `strftime.c`, `strptime.c`, and `zdump.c`.

## NetBSD Defaults
The header sets NetBSD-oriented defaults:
- `TM_GMTOFF` maps to `tm_gmtoff`.
- `TM_ZONE` maps to `tm_zone`.
- `STD_INSPIRED` and `NETBSD_INSPIRED` default enabled.
- Runtime leap seconds default enabled through `TZ_RUNTIME_LEAPS`.
- `HAVE_LONG_DOUBLE`, `HAVE_GETEUID`, `HAVE_GETRESUID`, `HAVE_LINK`, `HAVE_SETENV`, and similar capability macros default to available unless configured otherwise.

It also supports host-tool builds through optional `nbtool_config.h`.

## Portability Layer
The file establishes feature-test macros before system headers, including `_GNU_SOURCE`, `_POSIX_PTHREAD_SEMANTICS`, `__EXTENSIONS__`, Windows nonstandard-name exposure, and `_TIME_BITS=64` when compatible with `_FILE_OFFSET_BITS=64`.

It supplies fallbacks or detection for:
- `bool` and `static_assert`.
- C89/C99 integer typedefs and format macros under `PORT_TO_C89`.
- `strnlen`, `mempcpy`, `getopt`, `environ`, and errno constants.
- Checked arithmetic via C23 `<stdckdint.h>` or compiler builtins.
- Compiler attributes such as deprecated, fallthrough, maybe-unused, noreturn, format, const, pure, nonstring, and tzcode-specific GCC bug workarounds.

## API Renaming and Time Type Support
The `TZ_TIME_T` machinery allows tzcode to be built with a private `time_t` type or non-POSIX epoch configuration. When active, the header renames standard APIs to `tz_*` equivalents and declares the renamed functions. This supports testing unusual `time_t` widths, signedness, local epochs, and reserved external identifiers.

It also declares or exposes:
- Standard-like APIs: `gmtime`, `localtime`, `mktime`, `timegm`, `strftime`, `tzset`, etc.
- STD-inspired APIs: `tzsetwall`, `offtime`, `offtime_r`, `timelocal`, `timeoff`, `time2posix`, `posix2time`.
- NetBSD timezone-object APIs: `timezone_t`, `localtime_rz`, `mktime_z`, `tzalloc`, `tzfree`, `posix2time_z`, `time2posix_z`.

## Integer and Time Helpers
Defines:
- `TYPE_BIT`, `TYPE_SIGNED`, `TWOS_COMPLEMENT`.
- `MAXVAL`, `MINVAL`, `TIME_T_MIN`, `TIME_T_MAX`.
- `INT_STRLEN_MAXIMUM`.
- `INDEX_MAX` for safely bounded object sizes.
- `INITIALIZE` for compiler-warning suppression.
- `UNINIT_TRAP` control for whether mktime-style heuristics can read uninitialized `struct tm` fields.

These macros underpin overflow-sensitive calculations in `localtime.c`, `%s` formatting in `strftime.c`, and range scanning in `zdump.c`.

## Calendar Constants
Defines core calendar constants when not already present:
- Seconds/minutes/hours/day/week constants.
- `DAYSPERNYEAR`, `DAYSPERLYEAR`, `MONSPERYEAR`, `YEARSPERREPEAT`.
- `SECSPERDAY`, `DAYSPERREPEAT`, `SECSPERREPEAT`, `AVGSECSPERYEAR`.
- `years_of_observations`.
- `TM_SUNDAY` through `TM_SATURDAY`, `TM_JANUARY` through `TM_DECEMBER`.
- `TM_YEAR_BASE`, `TM_WDAY_BASE`, `EPOCH_YEAR`, `EPOCH_WDAY`.
- `isleap` and `isleap_sum`.

## libc Internal Hooks
Under `_LIBC`, includes `reentrant.h` and declares internal shared symbols from `localtime.c`: `__lcl_ptr`, `__lcl_get_monotonic_time`, `__lcl_lock`, `__lcl_unlock`, and `tzset_unlocked`. These are used by `strftime.c` to synchronize with local timezone state.

## Notable Risks and Edge Cases
- This header intentionally mutates namespace and type behavior through macros; include order is critical.
- Many defaults are portability heuristics and may differ for host-tool, libc, and standalone builds.
- `TIME_T_MIN/MAX` depend on assumptions about padding and signed integer representation, guarded by static assertions where possible.
- API renaming under `TZ_TIME_T` can make symbol identity non-obvious during debugging.
