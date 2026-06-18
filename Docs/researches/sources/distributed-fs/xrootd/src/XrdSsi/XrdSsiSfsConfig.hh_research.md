# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSfsConfig.hh

## Purpose
`XrdSsiSfsConfig.hh` declares the configuration driver for the SSI filesystem/stat plugins. It owns parsed library paths, directive parameters, runtime role metadata, and the setup methods that build global SSI runtime state.

## Important APIs and Types
The public API is two `Configure` overloads and constructor/destructor. Public fields expose version, host/program/instance names, role, CMS cluster pointer, port, and mode flags (`isServer`, `isCms`). Private parsing/configuration methods match the directives handled in the `.cc` file.

## Control Flow
An instance is constructed with defaults derived from environment variables. `Configure(configFile, env)` parses the file and then calls `Configure(env)`, which loads CMS/provider/service objects.

## State and Persistence
The object owns duplicated strings for config filename and library/parameter directives and frees them in the destructor. Global runtime state is defined in the implementation file; this header stores no persistent data.

## Dependencies and Integration Points
Forward declarations cover `XrdOucEnv`, `XrdOucStream`, `XrdSsiCluster`, `XrdSsiServer`, and `XrdVersionInfo`. The class is instantiated by `XrdSfsGetFileSystem2` and `XrdOssStatInfoInit2`.

## Risks and Test Signals
Because many fields are public, tests should verify constructor defaults and cleanup after partial configuration failures. Integration tests should confirm CMS mode uses lookup provider symbol while normal server mode requires a service object.
