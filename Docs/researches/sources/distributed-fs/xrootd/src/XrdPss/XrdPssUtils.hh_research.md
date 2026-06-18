# sources/distributed-fs/xrootd/src/XrdPss/XrdPssUtils.hh

## Purpose

`XrdPssUtils.hh` declares shared PSS helper functions and the inline forwarding-path test macro.

## Important APIs, Types, And Functions

- `XrdPssUtils::getDomain()`, `is4Xrootd()`, `valProt()`, and `Vectorize()` are stateless static helpers.
- `IS_FWDPATH(x)` detects path-encoded root/xroot forwarding forms such as `/root:/` and `/xroot:/`.

## Control Flow

The declared helpers are called by config and URL code. `IS_FWDPATH` is a raw macro that reads fixed offsets from its argument and should only be used on strings known to be long enough and slash-prefixed.

## State And Persistence

No state is declared in the header.

## Dependencies And Integration Points

The header includes `<vector>` and is included by PSS config and URL code. The macro encodes PSS forwarding semantics shared with path handling outside this subset.

## Risks And Edge Cases

- `IS_FWDPATH` performs unchecked pointer arithmetic and prefix reads.
- `Vectorize()` returns pointers into mutable caller storage, which the header comment documents but callers must honor.

## Test Signals

Compile tests should include the header in PSS users. Behavior tests should cover the macro on valid forwarding paths and ensure callers do not pass too-short strings.
