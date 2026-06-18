# sources/test-tools/strace/maint/update_copyright_years.awk

Purpose: awk helper that inserts a new copyright notice after an existing copyright block.

Important APIs/types/functions: external variables `COMMENT_MARKER`, `COMMENT_MARKER_RE`, `COPYRIGHT_MARKER`, and `COPYRIGHT_NOTICE`; state machine states 0 through 3; regexes for initial copyright lines and continuations.

Control flow: detect the beginning of a copyright notice, stay in the notice/continuation block while matching lines continue, transition after the block, print the new notice once, then print all input lines. END exits with `3 - state`, allowing caller to distinguish whether insertion happened.

State and persistence behavior: streaming only; writes transformed file to stdout.

Dependencies and integration points: called by `update_copyright_years.sh` when a file lacks an existing notice for the target owner.

Risks: continuation detection is comment-prefix sensitive and may insert in the wrong place for unusual copyright layouts. Exit-code protocol is non-obvious.

Test signals: files with C, roff, and shell comment styles should get a single inserted notice after existing copyright blocks.
