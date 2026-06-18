<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcAllowDecision.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcAllowDecision.cc

## Purpose

`XrdPfcAllowDecision.cc` implements the simplest decision plugin for XrdPfc: every path is allowed to be cached.

## Important APIs, Types, And Functions

- `AllowDecision` derives from `XrdPfc::Decision`.
- `Decide(std::string&, XrdOss&) const` always returns `true`.
- Exported `XrdPfcGetDecision(XrdSysError&)` creates a new `AllowDecision`.

## Control Flow

When configured as a decision library, `Cache::xdlib()` resolves `XrdPfcGetDecision`, stores the returned object, and later `Cache::Decide()` invokes `Decide()` for each candidate file. This plugin never rejects.

## State And Persistence

The plugin has no state and does not touch persistent storage.

## Dependencies And Integration Points

It depends on `XrdPfcDecision.hh` and `XrdSysError`. It is loaded dynamically through `XrdOucPinLoader` using the fixed exported symbol.

## Risks And Edge Cases

- This plugin provides no filtering and is mainly useful as an example or explicit allow-all policy.
- The `Decide` signature uses non-const `std::string&`, differing from the base declaration's const reference in the header; it still compiles here only if the effective declaration matches through permissive overload behavior would be risky. In this source, `virtual bool Decide(std::string &, XrdOss &) const` should be checked against the base `const std::string&` contract.

## Test Signals

Tests should load the module, resolve `XrdPfcGetDecision`, call `ConfigDecision()` through the base default, and verify `Decide()` returns true for arbitrary paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcAllowDecision.cc -->
