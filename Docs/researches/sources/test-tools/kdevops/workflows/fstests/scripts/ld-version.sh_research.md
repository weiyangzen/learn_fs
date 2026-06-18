## sources/test-tools/kdevops/workflows/fstests/scripts/ld-version.sh

Purpose: Converts a linker/tool version string from stdin into a comparable integer version code.

Important APIs/types/functions: This AWK script strips prefixes/suffixes, splits the first remaining token on `.`, and prints `major*100000000 + minor*1000000 + patch*10000`.

Control flow: It processes the first input record only, normalizes strings that include `version ` or parenthesized prefixes, emits one numeric value, and exits.

State and persistence: Stateless; no files are read or written beyond stdin/stdout.

Dependencies and integration points: Used by `oscheck.sh` to compare filesystem tool versions such as xfsprogs, btrfs-progs, e2fsprogs, and reiserfs tools.

Risks and test signals: Missing patch components become zero/empty AWK arithmetic, which is usually acceptable but should be tested for two-component versions. Test with version samples like `4.15.1`, `mke2fs 1.47.0`, and vendor-suffixed strings.
