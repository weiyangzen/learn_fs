# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t10.l

Single-line diff regression fixture.

Key behavior:
- Contains the text `a line of text`.
- The stored file is 14 bytes and has no terminating newline, making it useful for testing final-line newline diagnostics.

Research notes:
- This fixture exercises `fetch` behavior for “No newline at end of file”.
