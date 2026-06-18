# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/conv_ksc.c

Korean EUC/KSC converter for `tcs`.

Key functions:
- `ukscproc` decodes ASCII and codeset-1 two-byte KSC 5601 characters. Backslash maps to U+20A9 when `korean646` is enabled.
- `uksc_in` streams bytes through `ukscproc`.
- `uksc_out` builds reverse mapping from `tabksc5601`, emits ASCII directly, and emits EUC-style two-byte codes with high bits set.

Notable behavior:
- Codeset 2/3 handling is present only as commented-out state names and transitions.
- EOF in the middle of a two-byte character produces a diagnostic and substitutes a fallback second byte.
