# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfmd5.c

## Purpose
Registers the `MD5Encode` write filter.

## Key Functions
- `zMD5E()` delegates directly to `filter_write_simple()` with `s_MD5E_template`.

## Important Behavior
- Only an encoder is registered; there is no MD5 decode counterpart.

## Research Notes
Thin filter registration file.
