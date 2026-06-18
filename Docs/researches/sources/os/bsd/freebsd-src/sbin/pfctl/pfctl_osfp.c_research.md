# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_osfp.c

## Purpose

`pfctl_osfp.c` implements passive OS fingerprint management for pfctl. It parses fingerprint files, loads fingerprints into the kernel, imports active fingerprints from the kernel, maintains local name-to-ID trees, resolves fingerprint names used in rules, and prints fingerprint data.

It handles PF OS fingerprint identities as a hierarchy:
- class
- version
- subtype

## Data Structures

`struct name_entry` stores one class/version/subtype name:
- `nm_num`: numeric ID assigned for PF packing.
- `nm_name`: display/lookup name.
- `nm_sublist`: nested list for versions or subtypes.
- `nm_sublist_num`: next numeric ID within that sublist.

Global state:
- `classes`: root list of OS classes.
- `class_count`: assigned class count.
- `fingerprint_count`: total loaded/imported fingerprints.

## Loading Fingerprints From File

`pfctl_file_fingerprints()`:
1. Flushes pfctl’s local fingerprint view.
2. Opens the fingerprint file with `pfctl_fopen()`.
3. Clears kernel fingerprints unless in no-action mode.
4. Reads each line with `fgetln()`.
5. Removes comments and leading/trailing whitespace.
6. Parses colon-separated fields:
   - window size
   - TTL
   - don’t-fragment flag
   - packet size
   - TCP options
   - OS class
   - OS version
   - OS subtype
   - OS description
7. Parses TCP option signatures with `get_tcpopts()`.
8. Converts modifiers into `PF_OSFP_*` flags.
9. Adds the IPv4 fingerprint.
10. Also adds an IPv6-adjusted fingerprint by setting `PF_OSFP_INET6`, forcing DF, and adjusting packet size by the IPv6/IPv4 header size difference.

The parser accepts modifiers such as:
- `*`: don’t care
- `%`: modulus
- `S`: MSS multiple
- `T`: MTU multiple

## Kernel Operations

- `pfctl_clear_fingerprints()` calls `DIOCOSFPFLUSH`.
- `add_fingerprint()` calls `DIOCOSFPADD` unless in no-action mode.
- `pfctl_load_fingerprints()` repeatedly calls `DIOCOSFPGET` until `EBUSY` signals completion, importing each fingerprint locally.

There is also a `FAKE_PF_KERNEL` path where `pf_osfp_add()` is called directly instead of ioctl.

## Local Fingerprint Model

`pfctl_flush_my_fingerprints()` recursively frees the local class/version/subtype lists and resets counts.

`fingerprint_name_entry()` finds or creates a name in a list. Existing entries are moved to the front. Empty or null names return `NULL`, allowing version/subtype to be optional.

`import_fingerprint()` imports kernel-provided packed IDs and names into the local hierarchy while preserving maximum assigned numeric IDs.

`add_fingerprint()` assigns numeric IDs for class/version/subtype names, expands version/subtype ranges, packs them into `fp_os.fp_os`, increments the count, and loads the signature.

The range expansion macro accepts compact ranges like `1-4` or `2.2-2.6` and recursively creates one fingerprint per expanded value with `PF_OSFP_EXPANDED`.

The class name `nomatch` is reserved and rejected.

## Lookup By Name

`pfctl_get_fingerprint(name)` resolves rule syntax into a packed `pf_osfp_t`:
- `"unknown"` maps to `PF_OSFP_UNKNOWN`.
- A bare class name maps to class plus wildcard version/subtype.
- Otherwise it parses `class version subtype`.
- It supports fuzzy matching for version/subtype strings joined by `.`, space, tab, or `-`.

After packing, it unpacks again to detect overflow of class/version/subtype bit fields. If packing would collide with `PF_OSFP_ANY` or overflow, it returns `PF_OSFP_NOMATCH`.

## Lookup By ID

`pfctl_lookup_fingerprint(fp, buf, len)` converts a packed fingerprint ID back to text:
- `PF_OSFP_UNKNOWN` becomes `unknown`.
- `PF_OSFP_ANY` becomes `any`.
- Known class/version/subtype IDs are rebuilt as text.
- Missing or invalid IDs become `nomatch`.

The formatting preserves common version/subtype separators, using `.` when the version contains a dot and subtype begins with a digit.

## Listing And Sorting

`pfctl_show_fingerprints()`:
- In `-s all` mode, prints a section title and total fingerprint count.
- Otherwise prints a class/version/subtype table.

`sort_name_list()` recursively sorts each name list case-insensitively. The implementation is intentionally simple and slow, but fingerprint lists are small enough for that to be acceptable.

`print_name_list()` recursively prints the hierarchy with tab-separated prefixes.

## Parsing Helpers

`get_field()` returns the next colon-separated field from a line, trimming trailing whitespace.

`get_str()` copies the next field into allocated memory and enforces a minimum length.

`get_int()` parses integer fields with optional modifiers and max bounds, producing field-specific diagnostics with file and line number.

`get_tcpopts()` parses compact TCP option syntax:
- `N`: NOP
- `S`: SACK
- `T` or `T0`: timestamp, optionally zero timestamp
- `M`: MSS, with optional `*` or `%`
- `W`: window scale, with optional `*` or `%`

It packs options into `pf_tcpopts_t` using `PF_OSFP_TCPOPT_BITS` and returns MSS/window-scale values plus modifier flags.

`print_ioctl()` reconstructs a textual representation of a `pf_osfp_ioctl`, mainly for debug output.

## Role In This Group

`pfctl_osfp.c` is a specialized parser/loader for PF passive OS detection signatures. It complements the main rule loader by making OS fingerprint names available to rules and by synchronizing the userland name hierarchy with kernel fingerprint IDs.
