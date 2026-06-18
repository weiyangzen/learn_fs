<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_error_common.py -->
# sources/user-network-fs/samba/source4/scripting/bin/gen_error_common.py

## Purpose

`gen_error_common.py` provides shared parsing helpers for generators that transform copied MS-ERREF error tables into Samba C, Python, or Rust definitions.

## Important APIs, Types, and Functions

`ErrorDef` stores `err_code`, `err_define`, `err_string`, `isWinError`, and source `linenum`. `escapeString()` prepares text for generated C strings. `parseErrorDescriptions()` parses table-like text into `ErrorDef` objects using a caller-provided transform function.

## Control Flow

The parser skips blank lines, starts a new error when a line begins with `0x`, treats the next non-code token as the symbolic name, appends later text as description, escapes strings, counts parsed lines, prints a summary, and returns the list.

## State and Persistence Behavior

All state is in-memory. No files are written by this helper.

## Dependencies and Integration Points

It is imported by `gen_hresult.py`, `gen_ntstatus.py`, and `gen_werror.py`.

## Risks and Edge Cases

Input parsing assumes a simple copied-table format. Lines before the first hex code are ignored. Description joining can blur table columns. It prints to stdout, which can be noisy in build logs.

## Test Signals

Unit tests should cover blank lines, missing descriptions, multiline descriptions, escaping quotes/tabs/backslash-angle text, and transform functions for HRESULT, NTSTATUS, and WERROR names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_error_common.py -->
