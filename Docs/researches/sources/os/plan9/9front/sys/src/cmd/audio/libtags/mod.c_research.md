# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/mod.c

## Role

This file detects ProTracker-style MOD module files and extracts their title.

## Main Interface

`tagmod(Tagctx *ctx)` seeks to offset 1080, reads the 4-byte module signature, compares it with a static list of known variants, then returns to the beginning and reads the 20-byte title.

## Format Detection

Recognized signatures include `M.K.`, `M!K!`, `M&K!`, `N.T.`, `NSMS`, `FLT4`, `FLT8`, `CD81`, `OCTA`, `OKTA`, `4CHN`, `6CHN`, `8CHN`, `10CH`, `16CN`, `32CN`, and a few NUL-padded variants.

## Output

The title is converted from CP437 to UTF-8 and emitted as `Ttitle`.

## Risks

This parser only checks a signature and title. It does not validate full module structure, so detection depends on the uniqueness of the signature at offset 1080.
