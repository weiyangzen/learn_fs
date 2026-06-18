# sources/sync-backup/borg/scripts/glibc_check.py

Purpose: Checks whether one or more binaries require no newer GLIBC symbol version than a specified target version.

Important APIs/types/functions: Uses `glibc_re = re.compile(r"GLIBC_([0-9]\.[0-9]+)")`, `parse_version(v)`, `format_version(version)`, and `main()`. External dependency is `objdump -T`.

Control flow: Parses target version from `sys.argv[1]`, runs `objdump -T` on each filename, extracts all `GLIBC_x.y` symbols, records each binary's maximum required version, computes the overall maximum, compares against target, prints diagnostics, and exits 0 for OK or 1 for not OK.

State and persistence: Read-only over binaries; no persistent output except stdout/stderr and process exit code.

Dependencies and integration points: Requires GNU binutils `objdump` and ELF binaries with GLIBC symbol versions. Useful after `fetch-binaries` or binary build scripts.

Risks: If `objdump` fails for every file, `overall_versions` is empty and `max(overall_versions)` raises `ValueError`. The regex only handles single-digit major/minor groups like `2.36`, which matches current glibc naming but is not fully general.

Test signals: Unit-test `parse_version`/`format_version`, run against known binaries requiring older/newer GLIBC than target, and test invalid/non-ELF input handling.
