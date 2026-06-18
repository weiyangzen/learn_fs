# sources/distributed-fs/xrootd/python/src/PyXRootDEnv.hh

## Purpose
This header implements module-level Python functions for interacting with the global XrdCl default environment and logging controls.

## Important APIs, Types, and Functions
`EnvPutString_cpp`, `EnvGetString_cpp`, `EnvPutInt_cpp`, `EnvGetInt_cpp`, `EnvGetDefault_cpp`, `XrdVersion_cpp`, `SetLogLevel_cpp`, and `SetLogMask_cpp` are Python C API functions registered by `PyXRootDModule.cc`.

## Control Flow
Each function parses Python arguments, reads or writes `XrdCl::DefaultEnv::GetEnv()`, and returns Python booleans, strings, ints, or `None`. `XrdVersion_cpp` strips a leading `v` from `XrdVERSION` once into a static string. Log functions call `DefaultEnv::SetLogLevel` or `SetLogMask` if parsing succeeds and always return `None`.

## State and Persistence
The functions mutate XrdCl's process-global default environment and logging configuration. Settings are in-memory and can affect all subsequent XrdCl operations in the process.

## Dependencies and Integration Points
Depends on `XrdClDefaultEnv` and `XrdVersion.hh`. Exposed as module-level helpers in the `client` extension.

## Risks and Test Signals
The log setters ignore parse failure by returning `None` instead of propagating an argument error. Environment writes may be rejected if shell-imported settings already exist, indicated by false return. Tests should verify put/get behavior, default lookup for string and integer defaults, version formatting, log setter argument validation, and cross-operation impact of environment changes.
