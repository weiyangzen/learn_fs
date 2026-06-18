# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t11.l

Large text diff fixture containing a Unix manual page for `ed`.

Key behavior:
- Begins with OpenBSD/NetBSD roff comments and `.TH ED 1 "21 May 1993"`.
- Covers `ed` synopsis, description, addressing, regular expressions, commands, diagnostics, and related manual sections.
- Ends with “but any changes to the buffer are lost.”

Research notes:
- The file is 1003 text lines with many roff macros and blank lines.
- It is a realistic long-form prose/manual input for testing large text diffs, context hunks, and line matching.
