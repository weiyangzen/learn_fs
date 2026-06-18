# sources/sync-backup/rsync/wildtest.c

Purpose: standalone test driver for rsync’s wildmatch implementation. It includes `lib/wildmatch.c` directly so the helper can exercise internal iteration counters and array matching.

Important APIs/functions: options are parsed with popt: `--iterations/-i`, `--empties/-e`, and `--explode/-x`. `run_test()` either calls `wildmatch(pattern, text)` or splits text into chunks/empty elements and calls `wildmatch_array()`. Optional `COMPARE_WITH_FNMATCH` can compare against libc `fnmatch()`. `main()` parses a test file where each non-comment line has two flags and two strings, handles quoting, and reports total wildmatch errors.

Control flow and state: global knobs control chunk size and inserted empty array elements. The parser is line-oriented and exits on syntax errors. Return status is zero even when mismatches are reported; wrappers check stdout.

Dependencies and integration: used by `wildmatch_test.py` with `wildtest.txt`. It depends on popt and rsync wildmatch code. Risks include fixed 2048-byte line buffer, direct inclusion of implementation, and stdout contract coupling. Test signal is the exact `No wildmatch errors found.` output across option sets.
