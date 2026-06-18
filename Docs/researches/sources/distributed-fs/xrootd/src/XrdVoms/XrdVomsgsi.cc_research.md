# sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsgsi.cc

## Purpose

This file is the externally loadable GSI VOMS plugin entry point. It bridges the historical XRootD GSI security plugin ABI to the `XrdVomsFun` implementation by exporting C-linkage functions named `XrdSecgsiVOMSFun` and `XrdSecgsiVOMSInit`.

## Important APIs, Types, and Functions

- `XrdSecgsiVOMSInit(const char *cfg)`: creates a process-global `XrdVomsFun` instance with a static `XrdSysLogger` and `XrdSysError` destination, then delegates configuration parsing to `XrdVomsFun::VOMSInit`.
- `XrdSecgsiVOMSFun(XrdSecEntity &ent)`: validates that initialization created `vomsFun`, then delegates credential extraction and entity mutation to `XrdVomsFun::VOMSFun`.
- Anonymous-namespace `XrdVomsFun *vomsFun`: plugin singleton used by both exported functions.

## Control Flow

Initialization is expected before credential processing. `XrdSecgsiVOMSInit` allocates `XrdVomsFun`, keeps it in the static pointer, and returns the result of `VOMSInit`. Later, the GSI layer calls `XrdSecgsiVOMSFun`, which returns `-1` when initialization has not happened and otherwise forwards the `XrdSecEntity` by reference.

## State and Persistence Behavior

State is process-local and static. The logger and error destination live for process lifetime, and every successful init overwrites `vomsFun` with a newly allocated object without deleting any previous object. Persistent configuration and mapfile behavior live in `XrdVomsFun`, not this file.

## Dependencies and Integration Points

The file depends on `XrdSysError`, `XrdSysLogger`, `XrdSecEntity` through the VOMS API, and `XrdVomsFun.hh`. Its exported symbol names are the integration surface for dynamic plugin loading and preserve backward compatibility with older GSI VOMS naming.

## Risks

- Repeated `XrdSecgsiVOMSInit` calls leak the prior `XrdVomsFun` object and replace global behavior.
- `XrdSecgsiVOMSFun` has no locking around `vomsFun`, so concurrent calls during reinitialization would race.
- Failure is compressed to `-1` before initialization; richer diagnostics depend on initialization logs in `XrdVomsFun`.

## Test Signals

Useful checks are dynamic loading symbol tests, invoking `XrdSecgsiVOMSFun` before init and expecting `-1`, init with valid and invalid VOMS config strings, and integration tests confirming `XrdSecEntity` fields are populated by the delegated implementation.
