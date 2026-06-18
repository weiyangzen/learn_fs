# sources/test-tools/stress-ng/stress-str.c

## Purpose

`stress-str.c` implements `str`, a CPU/cache/memory stressor for libc string functions. It generates deterministic-looking random strings from disjoint alphabets and repeatedly calls selected string APIs, optionally verifying expected results and collecting per-method call-rate metrics.

## Important APIs, Types, and Functions

- `stress_str_args_t` carries the selected libc function pointer, method name, source strings, lengths, destination buffer, and failure flag.
- `stress_str_func` and `stress_str_method_info_t` define the common method interface and method table.
- `stress_rndstr_case()` fills a buffer with random uppercase-like or lowercase-like characters and terminates it, avoiding `+` so search-negative checks are stable.
- `strchk()` and `STRCHK` report verification failures when `--verify` is enabled.
- Method functions cover `strcasecmp`, `strncasecmp`, `index`, `rindex`, `strlcpy` or `strcpy`, `strlcat` or `strcat`, `strncat`, `strchr`, `strrchr`, `strcmp`, `strncmp`, `strcoll`, `strlen`, and `strxfrm`, depending on build features.
- `stress_str_all()` rotates through all methods except the special `all` entry and records per-method metrics.
- `stress_str()` parses the method, initializes buffers, alternates generated strings, calls the selected method in a loop, swaps string buffers, records metrics, and returns failure if verification detected any mismatch.

## Control Flow

The stressor selects a method from `str-method`, initializes `str1`, `str2`, and `strdst` stack buffers, generates the first string, zeros the metrics array, synchronizes, and enters the run loop. Each iteration generates `str2` with the opposite alphabet case, times one call to the selected method function, adds the method's reported call count to metrics, then swaps `str1`/`str2` and their lengths so subsequent iterations cover both buffer sizes.

Each method runs a tight loop over offsets or string lengths while the global continue flag remains set. Verification checks include equality on identical strings, inequality across disjoint alphabets and shifted pointers, negative search for `+`, positive search for known first characters, expected lengths, expected destination pointer returns, and expected `strl*` lengths where available. At shutdown the stressor emits one metric per method with nonzero duration, named "`<method> calls per sec`".

## State and Persistence Behavior

All strings and destination buffers are stack-local to the worker. The metrics array is static at file scope and process-local. No heap allocation, files, locale changes, or persistent state are created by this stressor. Locale-dependent functions such as `strcoll()` and `strxfrm()` use the process's current locale.

## Dependencies and Integration Points

The file depends on libc string APIs and stress-ng option parsing, metrics, random generator, continue flags, state transitions, and verification flags. Some methods are conditional on `strings.h`, BSD `strlcpy`/`strlcat`, static build mode, `index`, and `rindex`. It registers as `CLASS_CPU | CLASS_CPU_CACHE | CLASS_MEMORY | CLASS_HOT`, `VERIFY_OPTIONAL`, with `max_metrics_items` equal to the method table size.

## Risks and Edge Cases

The method table intentionally swaps between BSD `strl*` and standard `str*` implementations depending on availability, so metric names and semantics differ by build. Verification assumptions rely on the uppercase and lowercase alphabets having no overlapping characters and excluding `+`. `strcoll()` and `strxfrm()` can be locale-sensitive; the disjoint alphabets make inequality likely but locale behavior should be considered when changing alphabets. The `stress_bogo_add()` calls add fixed small counts rather than the full local operation count; metrics carry the detailed call counts.

## Test Signals

Expected test signals include successful `--str-method all`, individual method selection, per-method call-rate metrics, and verification failure reporting when expectations are broken. Build tests should cover systems with BSD `strlcpy`/`strlcat`, systems without `strings.h` aliases, and static builds where BSD `strl*` methods are excluded.
