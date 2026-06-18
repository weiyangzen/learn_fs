# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucBackTrace.cc

## Purpose
Implements optional debugging backtraces with filters by pointer, XRootD request code, and response/status code.

## Important APIs and control flow
Static request/response tables map protocol names to numeric codes and bit masks. `Init()` populates request and response filters from explicit strings or `XRDBT_REQFILTER`/`XRDBT_RSPFILTER`, using `XrdOucTokenizer`. `Filter()` manages pointer filters for `this` or object pointers under `btMutex`, supporting add, clear, delete, and replace actions while `xeqPtrFilter` provides a fast atomic indication that any pointer filters exist.

`DoBT()` applies pointer filters unless forced, formats a `TBT` header with thread id and pointers, calls `DumpStack()`, and writes to `std::cerr`. `XrdBT()` additionally applies request/response filters. `DumpStack()` uses `backtrace()` and `backtrace_symbols()` except on musl, demangles C++ symbols with `abi::__cxa_demangle`, and limits depth using `XRDBT_DEPTH` capped at 30.

## State, dependencies, and integration
State is process-global filter vectors and bit masks. Dependencies include XRootD protocol constants, tokenizer, atomics, pthread mutex helpers, platform thread IDs, and glibc/macos backtrace APIs.

## Risks and test signals
`Filter(delIt)` emits an unconditional `std::cerr` debug line, which may be unintended in production. `backtrace_symbols()` output is not freed, creating a small allocation leak per dump. Tests should validate filter truth tables, env-var parsing, forced traces, musl fallback, depth capping, and request/response code mappings.
