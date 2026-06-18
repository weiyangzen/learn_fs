# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t15.l

Tiny numeric fixture.

Key behavior:
- Contains visible lines `1`, `2`, and `3`.
- The file is 5 bytes, with the final line lacking a trailing newline.

Research notes:
- Likely paired with `diff-t14.l` to test final-line insertion and no-newline reporting.
