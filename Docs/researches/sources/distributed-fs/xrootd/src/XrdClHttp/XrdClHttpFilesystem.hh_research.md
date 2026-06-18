# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFilesystem.hh

## Purpose
`XrdClHttpFilesystem.hh` declares `XrdClHttp::Filesystem`, the final HTTP implementation of `XrdCl::FileSystemPlugIn`.

## Important APIs and Types
The class overrides filesystem methods for `DirList`, `GetProperty`, `Locate`, `MkDir`, `Rm`, `RmDir`, `SetProperty`, `Stat`, and `Query`. Private helpers return a connection callout function pointer, determine whether to send extended response info, and build the current operation URL from base URL plus properties.

## Control Flow
The declaration establishes a thin enqueueing object: public methods translate XrdCl filesystem calls into concrete curl operations, while properties modify callouts and URL construction.

## State and Persistence
State consists of a shared handler queue, atomic header callout pointer, logger, base URL, and property map protected by shared mutex. Persistent remote effects happen in implementation methods via HTTP verbs.

## Dependencies and Integration Points
The file depends on connection/header callout public interfaces, XrdCl filesystem/log/plugin/URL headers, and STL shared mutex and property containers. It is created by `Factory::CreateFileSystem`.

## Risks and Test Signals
The primary risk is property concurrency and raw callout pointer lifetime. Tests should verify property get/set with concurrent reads, URL building from root and nested paths, response-info behavior, and that methods return `errOSError` when queue submission throws.
