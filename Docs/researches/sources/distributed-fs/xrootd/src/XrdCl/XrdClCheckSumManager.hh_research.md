# sources/distributed-fs/xrootd/src/XrdCl/XrdClCheckSumManager.hh

## Purpose

This header declares `CheckSumManager`, the checksum calculator manager used by the XrdCl default environment. It provides calculator factory access and a local-file checksum helper.

## Important APIs, types, and functions

`GetCalculator(const std::string&)` returns a newly allocated `XrdCksCalc` for the requested algorithm or `0` on failure. `Calculate(XrdCksData&, const std::string&, const std::string&)` computes an algorithm-specific checksum over a file path and stores the result in `XrdCksData`.

The private `CalcMap` stores algorithm names to calculator prototypes, `pLoader` points to the plugin loader, and `pMutex` protects the prototype cache. Copy construction and assignment are declared private and not implemented.

## Control flow

Callers usually reach this manager through `DefaultEnv::GetCheckSumManager()`. They request calculators for streaming helpers or ask it to calculate a whole local file checksum. The implementation handles built-ins and dynamic plugin loading.

## State and persistence behavior

The manager stores process-local prototype calculators and a loader. There is no persistence, but the cache persists until `DefaultEnv` cleanup deletes the manager.

## Dependencies and integration points

The header depends on `<map>`, `<string>`, `XrdSysPthread`, and `XrdCksData`. It forward-declares `XrdCksLoader` and `XrdCksCalc`. Integration is with `DefaultEnv`, `CheckSumHelper`, `Utils`, and `ClassicCopyJob`.

## Risks and edge cases

The caller ownership contract for `GetCalculator` is documented but easy to violate. The manager is non-copyable by private declaration, but the header predates modern `= delete`, so diagnostics may be less clear. Algorithm name normalization is not centralized here.

## Test signals

Compile-time users include `DefaultEnv`, `CheckSumHelper`, `Utils`, and `ClassicCopyJob`. Runtime tests should assert calculator ownership, failure handling, and built-in algorithm availability.
