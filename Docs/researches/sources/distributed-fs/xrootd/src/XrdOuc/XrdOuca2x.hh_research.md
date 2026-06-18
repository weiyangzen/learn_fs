<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOuca2x.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOuca2x.hh

## Purpose

`XrdOuca2x.hh` declares the static conversion utility class used by XRootD configuration code to parse human-entered numbers, modes, sizes, ports, times, percentages, and hex/binary strings.

## Important APIs, Types, And Functions

- Public parsers: `a2i`, `a2ll`, `a2fm`, `a2p`, `a2sn`, `a2sp`, `a2sz`, `a2tm`, and `a2vp`.
- Public encoders/decoders: `b2x` and `x2b`.
- Private `Emsg()` overloads centralize formatted error reporting for `double`, `int`, and `long long` bounds.

## Control Flow

The class is a namespace-like holder of static methods. Callers pass a logger, an error-message prefix, source text, output storage, and optional bounds. The implementation logs failures and returns `-1`; successful conversions store through the output pointer and return `0`, except `a2p()` returns the parsed port number or `0` for allowed `any`.

## State And Persistence

The header declares no state and no object instances. All persistence is in caller-owned output variables.

## Dependencies And Integration Points

It includes `XrdSys/XrdSysError.hh` and is a common dependency of server, plugin, and cache configuration parsers.

## Risks And Edge Cases

- Mixed return conventions make `a2p()` different from the other `a2*` routines.
- Percentage values are represented by negative integers/long longs, an implicit API contract.
- The header does not document accepted suffixes; consumers need implementation knowledge or external docs.

## Test Signals

Compile and behavior tests should verify each declaration links to the implementation and that callers handle `a2p()` and negative percentage conventions correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOuca2x.hh -->
