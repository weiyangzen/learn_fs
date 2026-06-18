# sources/distributed-fs/xrootd/src/XrdPss/XrdPssUtils.cc

## Purpose

`XrdPssUtils.cc` implements small protocol and string helpers used by PSS configuration and URL handling.

## Important APIs, Types, And Functions

- Static protocol table recognizes `https://`, `http://`, `roots://`, `root://`, `xroots://`, `xroot://`, `pelican://`, and `s3://`.
- `getDomain(hName)` returns the substring after the first dot, or the whole hostname when no dot exists.
- `is4Xrootd(pname)` detects root/xroot-family protocol names.
- `valProt(pname, plen, adj)` validates a protocol prefix and returns the canonical table entry while reporting matched length.
- `Vectorize(str, vec, sep)` splits a mutable string in-place on a separator and rejects empty components.

## Control Flow

Callers pass raw strings. `valProt()` scans the table in order and can match shortened entries by subtracting `adj` from the required prefix length; `xorig()` uses this for forwarding protocol lists that omit URL punctuation. `Vectorize()` repeatedly replaces separators with NUL bytes and stores pointers into the original buffer.

## State And Persistence

Only static immutable protocol metadata is stored. `Vectorize()` mutates caller-owned memory and returns borrowed pointers into that buffer.

## Dependencies And Integration Points

The file depends on C string routines and is used by `XrdPssConfig.cc` for origin and forwarding protocol validation and by `XrdPssUrlInfo.cc` for CGI behavior.

## Risks And Edge Cases

- `Vectorize()` rejects trailing separators and empty elements but leaves the input partially modified on failure.
- `getDomain()` is a simple first-dot split and does not handle FQDN trailing dots, public suffixes, or null input.
- `valProt()` with `adj` can match abbreviated prefixes; callers must choose `adj` carefully.

## Test Signals

Tests should cover all supported protocol prefixes, unsupported strings, `xroot` vs non-xroot classification, forwarding lists with empty/trailing components, and hostnames with/without dots.
