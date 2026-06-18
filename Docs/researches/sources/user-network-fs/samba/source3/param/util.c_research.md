# sources/user-network-fs/samba/source3/param/util.c

Purpose: tiny helpers for extracting values from strings shaped like `parameter = value`.

Important APIs: `get_int_param()` returns `atoi()` of the substring after the first `=`, or `0` if absent. `get_string_param()` returns a pointer to the substring after the first `=`, or `NULL` if absent.

State and persistence: stateless; no allocation and no mutation.

Dependencies and integration: declared in `loadparm.h`, built as `PARAM_UTIL`, and likely used by older parameter parsing code that already has raw assignment strings.

Risks: no whitespace trimming, quoting, overflow detection, base handling, or error distinction between missing/invalid and integer zero. Returned string points into caller-owned input.

Test signals: inputs with no equals, empty values, whitespace, negative/large integers, and multiple equals.
