# File Research: sources/os/bsd/netbsd-src/lib/libintl/sysdep.c

Provides system-dependent gettext string expansion support.

It defines a sorted table mapping `inttypes.h` printf/scanf macro names, such as `PRId64` and `SCNxPTR`, to their platform-specific string expansions. `__intl_sysdep_get_string_by_tag` uses `bsearch` to resolve a tag and returns the expansion plus length, or an empty string if unknown.

Used by `.mo` sysdep string expansion in `gettext.c`.
