# sources/test-tools/kdevops/scripts/spdxcheck.py

## Purpose
Validates SPDX license identifiers in source file headers against license metadata from a kernel-style `LICENSES` tree.

## Important APIs and types
`SPDXdata` stores license and exception identifiers. `read_spdxdata(repo)` loads `LICENSES/preferred` metadata from the Git tree. `id_parser` is a PLY lexer/parser for SPDX expressions with tokens `ID`, `EXC`, `AND`, `OR`, `WITH`, `LPAR`, and `RPAR`. It validates identifiers and exception/license compatibility. `parse_lines(fd, maxlines, fname)` scans file headers for `SPDX-License-Identifier:`. `scan_git_tree()` and `scan_git_subtree()` walk GitPython tree objects.

## Control flow
CLI arguments select paths, stdin, or full tree scan. The script opens the current directory as a Git repository, reads SPDX metadata, constructs the parser, then scans up to `--maxlines` lines per file. It prints parse errors with file, line, column, message, and token; verbose mode prints counters.

## State and dependencies
Runtime state is in parser counters and SPDX lists. Dependencies are GitPython (`git`) and PLY (`ply.lex`, `ply.yacc`), plus a kernel-like `LICENSES` layout.

## Integration points
Used as a style/compliance checker in kernel-derived projects. It excludes the `LICENSES` tree and `license-rules.rst`.

## Risks and test signals
Only `LICENSES/preferred` is enabled, with dual/deprecated/exception directory support commented out. A bug path in `parse_lines` can reference `col` when `pe.tok` is false. Test with valid IDs, invalid IDs, invalid `WITH` exceptions, stdin mode, subtree mode, and `--verbose` counters.
