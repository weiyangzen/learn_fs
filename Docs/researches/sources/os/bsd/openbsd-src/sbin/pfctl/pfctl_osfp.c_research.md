# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_osfp.c

`pfctl_osfp.c` handles passive OS fingerprint loading, parsing, importing, lookup, and display for PF. It parses `/etc/pf.os`-style colon-delimited fingerprint records, maintains a local hierarchy of OS class/version/subtype names, packs those names into PF OS fingerprint ids, and syncs fingerprints to or from the kernel through OSFP ioctls.

Primary responsibilities:
- Parses fingerprint files in `pfctl_file_fingerprints()`.
- Clears kernel fingerprints with `DIOCOSFPFLUSH` and local fingerprints by recursively freeing the `classes` name tree.
- Loads active kernel fingerprints through repeated `DIOCOSFPGET` calls until kernel indicates completion.
- Shows fingerprints as class/version/subtype trees.
- Resolves string names to packed `pf_osfp_t` ids and packed ids back to printable names.
- Adds fingerprints to kernel with `DIOCOSFPADD`, or to fake-kernel test builds via `pf_osfp_add()`.

Data model:
- `struct name_entry` nodes form nested `LIST` trees: classes contain versions, versions contain subtypes.
- Each name entry has a numeric id assigned on first insert/import.
- Global `classes`, `class_count`, and `fingerprint_count` track current local state.
- PF ids are packed/unpacked through PF OSFP macros and validated against class/version/subtype bit widths.

File parsing:
- Each nonblank, noncomment line is split into fields: window size, TTL, DF, packet size, TCP options, OS class, version, subtype, and description.
- Integer fields support modifiers such as don't-care, MSS multiple, MTU multiple, and modulus where allowed.
- TCP options support NOP, SACK, timestamp, MSS, and window scale, with support for wildcard/modulus MSS and window scale.
- For each IPv4 fingerprint, the loader also creates an IPv6 variant by setting `PF_OSFP_INET6`, forcing DF, and adjusting packet size for IPv6 header length.
- Class names starting with `@` are generic; names starting with `*` suppress detail.

Lookup behavior:
- `pfctl_get_fingerprint()` recognizes `"unknown"`, direct class-only names, class/version names, and class/version/subtype names.
- It performs fuzzy subtype matching for common version-subtype separators such as `.`, whitespace, tab, and `-`.
- `pfctl_lookup_fingerprint()` prints `"unknown"`, `"any"`, `"nomatch"`, or a reconstructed class/version/subtype string with separator heuristics.
- Version and subtype ranges like `2.0-2.4` can be expanded by `add_fingerprint()` into multiple fingerprints.

Integration points:
- Called by `pfctl.c` before showing rules and when loading the main ruleset from `PF_OSFP_FILE`.
- Called by parser/rule printing through `pfctl_get_fingerprint()` and `pfctl_lookup_fingerprint()`.
- Uses `pfctl_fopen()` to reject directories as fingerprint input.
- Depends on PF OSFP kernel structures and ioctls from `<net/pfvar.h>`.

Notable risks and edge cases:
- Parsing is permissive about comments/whitespace but strict about field count and field-specific modifiers.
- `get_tcpopts()` stops at `PF_OSFP_MAX_OPTS`; extra option text beyond that can be accepted only as far as parsing permits.
- Duplicate kernel signatures are reported as warnings, while most other add failures are fatal.
- `pfctl_get_fingerprint()` warns and returns no match if packed ids overflow allocated bit fields.
