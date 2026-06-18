# sources/test-tools/crashmonkey/find_diff.sh

Purpose: parses a CrashMonkey diff file to print concise bug details and update bug-type counters. It distinguishes metadata/content mismatches from missing-file failures.

Important APIs/types/functions: input `_file`, counters `bugs`, `missing`, `stat`, patterns `DIFF: Content Mismatch` and `Failed stating`, arrays for inode/size/blocksize/block count/link count, `grep`, `cut`, and `tput`.

Control flow: validates the file, increments total bug count, scans each line. On metadata mismatch it captures paired actual/expected fields; on missing-file text it prints subsequent lines. After scanning, it increments the metadata or missing counter and prints the first differing metadata attribute.

State/persistence behavior: updates plain counter files in the current directory and prints diagnostic output. Dependencies/integration: sourced by `copy_diff.sh` during demo mode and assumes CrashMonkey diff formatting.

Risks/test signals: numeric comparisons assume captured fields are present and numeric, arrays hold only the first pair of entries, and unquoted variables can break on whitespace. It does not update `others` despite demo summary reading that file.
