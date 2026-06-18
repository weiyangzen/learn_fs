# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoTrace.hh

## Purpose

`XrdCryptoTrace.hh` defines tracing macros for the crypto subsystem around the global `cryptoTrace` pointer and trace masks from `XrdCryptoAux.hh`.

## Important APIs and Types

Macros include `QTRACE`, `PRINT`, `TRACE`, `DEBUG`, and `EPNAME` when `NODEBUG` is not defined. In no-debug builds they expand to no-ops. `cryptoTrace` is declared as an external `XrdOucTrace *`.

## Control Flow

Call sites set `EPNAME()` and then use trace macros. `PRINT()` writes through `cryptoTrace->Beg()`/`End()` and `std::cerr` when tracing is initialized.

## State and Persistence Behavior

Runtime trace state is process-global through `cryptoTrace` and its `What` mask. This header itself owns no state.

## Dependencies and Integration Points

It depends on `XrdOucTrace`, `XrdCryptoAux.hh`, and `XrdSysHeaders` in debug builds. It is used by factory, X.509, and request/chain code.

## Risks and Edge Cases

Trace expressions must not carry side effects because they disappear under `NODEBUG`. `PRINT()` silently does nothing when `cryptoTrace` has not been initialized by `XrdCryptoSetTrace()`.

## Test Signals

Build tests should compile with both debug and `NODEBUG`. Runtime tests should initialize trace flags and verify category filtering.
