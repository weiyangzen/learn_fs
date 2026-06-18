# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsFSctl_PI.hh

## Purpose

This header defines the plugin interface for customizing OFS `FSctl()` behavior. It is loaded through the `ofs.ctllib` directive and supports both file-scoped and filesystem-scoped control operations.

## Important APIs, types, and functions

`XrdOfsFSctl_PI::Plugins` passes loaded authorization, CMS, OSS, and SFS/OFS plugin pointers into `Configure()`. `Configure()` is virtual and defaults to success. Two pure virtual `FSctl()` overloads must be implemented: the legacy file version taking `cmd`, raw args, an `XrdSfsFile`, and error info; and the v2 filesystem version taking `cmd`, `XrdSfsFSctl`, and error info.

The protected `prvPI` pointer supports stacked plugins, and `eDest` gives plugins the configured logger.

## Control flow

`XrdOfsConfigPI` loads a concrete object named `XrdOfsFSctl`, sets `eDest` and `prvPI`, and later calls `Configure()` with the plugin bundle. Runtime OFS control methods call the appropriate virtual `FSctl()` overload when built-in handling does not apply.

## State and persistence behavior

The interface stores only stack linkage and logger pointer. Plugin implementations own any additional state or persistence.

## Dependencies and integration points

It forward-declares the major XRootD interfaces needed by FSctl plugins and documents the expected global instance name and optional `XrdVERSIONINFO` declaration. It integrates with `XrdOfsConfigPI`, `XrdOfs::FSctl()`, SFS file objects, and security identity.

## Risks and test signals

Plugins run inside the OFS process and receive unscreened argument strings for some commands, so interface tests should ensure authorization is performed by OFS before forwarding when required. Stacked plugins must explicitly forward through `prvPI` if desired. ABI tests should verify object name resolution, version declarations, `Configure()` ordering, and both overload contracts.
