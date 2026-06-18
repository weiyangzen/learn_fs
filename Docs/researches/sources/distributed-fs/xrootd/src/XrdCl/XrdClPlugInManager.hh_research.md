# sources/distributed-fs/xrootd/src/XrdCl/XrdClPlugInManager.hh

## Purpose

This header declares `PlugInManager`, the central registry that maps client URLs to plugin factories and owns dynamically loaded plugin libraries. It provides the public API used by the client environment and by programmatic plugin installers.

## Important APIs, Types, And Functions

Public methods are the constructor/destructor, `RegisterFactory(const std::string&, PlugInFactory*)`, `RegisterDefaultFactory(PlugInFactory*)`, `GetFactory(std::string)`, and `ProcessEnvironmentSettings()`. Private support includes `PlugInFunc_t`, `FactoryHelper`, `ProcessConfigDir`, `ProcessPlugInConfig`, `LoadFactory`, config-aware `RegisterFactory`, and `NormalizeURL`.

`FactoryHelper` owns `XrdOucPinLoader *plugin` and `PlugInFactory *factory`, records whether the entry came from environment/config (`isEnv`), and maintains a `counter` for shared helper entries.

## Control Flow

The public registration APIs normalize URLs and mutate the map under a mutex. Environment processing is a separate explicit call that can load a default plugin or scan config directories. Lookups return non-owned factory pointers. The private config registration path can associate one factory with multiple normalized URLs or install a config default for `url=*`.

## State And Persistence Behavior

`pFactoryMap` and `pDefaultFactory` are in-memory only. The manager owns factories and plugin loaders through `FactoryHelper`; callers do not own pointers returned by `GetFactory`. `pMutex` serializes access.

## Dependencies And Integration Points

The class depends on `XrdClPlugInInterface.hh`, `XrdOucPinLoader`, and `XrdSysMutex`. It is normally reachable through `DefaultEnv`, and plugin implementations must use the `PlugInFactory` ABI declared in the interface header.

## Risks And Edge Cases

The API uses raw factory pointers and ownership transfer, so callers must not delete registered factories. `GetFactory` takes `url` by value rather than const reference. Environment-derived factories are protected from programmatic replacement. A helper can be referenced by several map keys, making counter correctness central to safe destruction.

## Test Signals

Header-level contract tests should assert that registering null removes mappings/defaults, returned factories are non-owned, environment entries take precedence, and invalid URLs are rejected without altering existing state.
