<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/checkopts -->
# sources/user-network-fs/cifs-utils/checkopts

## Purpose

`checkopts` is a Python 3 maintenance script that compares CIFS mount options implemented by the kernel with options documented in `mount.cifs.rst`. It reports duplicated documentation, undocumented kernel options, documented-but-missing options, and negative options without positive counterparts.

## Important APIs, Types, and Functions

Key functions are `extract_canonical_opts`, `extract_kernel_opts`, `extract_man_opts`, `format_code`, `sortedset`, `opt_neg`, and `main`. The helper class `RX` wraps `re.search` while preserving the last match for easy capture access.

## Control Flow

`main` parses a kernel `connect.c` path and a mount manpage RST path. `extract_kernel_opts` scans `fsparam_*("name", enum, ...)` lines and later `case Opt_*` blocks to map option names to parser enums and implementation code. `extract_man_opts` scans the RST `OPTION` section and records short option declarations. `main` then computes set differences and alias/negation relationships before printing diagnostics.

## State and Persistence Behavior

The script is stateless except for local dictionaries and stdout output. It reads input files and does not modify them.

## Dependencies and Integration Points

It depends on Python 3 standard modules (`os`, `sys`, `re`, `subprocess`, `argparse`, `collections`). Its integration point is a developer workflow that has both the kernel CIFS parser source and cifs-utils manpage source available.

## Risks and Edge Cases

The parser is regex-based and tightly coupled to current kernel `fsparam_*` and `case Opt_*` formatting plus current RST option layout. It can miss options if macros span lines or documentation formatting changes. It compares names, not semantic behavior, so aliases and negative options need heuristics.

## Test Signals

Run the script against a known kernel CIFS `connect.c` and `mount.cifs.rst` and verify stable output. Unit tests can feed miniature kernel/manpage fixtures with aliases, negations, duplicate docs, ignored options, and malformed sections.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/checkopts -->
