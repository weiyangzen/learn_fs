# sources/distributed-fs/xrootd/src/XrdCl/XrdClPlugInManager.cc

## Purpose

This implementation manages runtime discovery, loading, registration, lookup, and cleanup of XrdCl client plugins. It supports programmatic registration, an environment-selected default plugin, config-directory plugin definitions, and an optional built-in erasure-coding plugin path under `WITH_XRDEC`.

## Important APIs, Types, And Functions

`RegisterFactory(url, factory)` registers or removes a programmatic factory for a normalized URL. `RegisterDefaultFactory(factory)` installs/removes a default factory. `GetFactory(url)` resolves URL-specific, protocol-specific, environment, and default factories. `ProcessEnvironmentSettings()` loads `PlugIn`/`PlugInConfDir` settings from `DefaultEnv`. `ProcessConfigDir` scans sorted `.conf` files. `ProcessPlugInConfig` parses mandatory `url`, `lib`, and `enable` keys. `LoadFactory` loads `XrdClGetPlugIn` via `XrdOucPinLoader`. The private `RegisterFactory(urlString, lib, factory, plugin)` handles semicolon-separated config URL registration and ownership sharing.

## Control Flow

Environment processing first checks `PlugIn`; if set, it attempts to load that library as a default factory and disables config scanning. Otherwise it scans `/etc/xrootd/client.plugins.d`, the user's `~/.xrootd/client.plugins.d`, and `PlugInConfDir`. Config files are processed alphabetically so later files can supersede earlier ones. Enabled config entries load a factory, disabled entries remove normalized mappings. Lookups prefer an environment default, then exact environment mapping, then protocol environment mapping, then programmatic default, exact mapping, protocol mapping.

## State And Persistence Behavior

`pFactoryMap` maps normalized URL/protocol strings to `FactoryHelper` objects. Helpers own a plugin loader and factory and carry `isEnv` plus a reference counter because one helper can be shared by multiple URL keys. `pDefaultFactory` owns the default helper. All public mutations and lookups are protected by `pMutex`. No registry state is persisted; config is reread only when `ProcessEnvironmentSettings` is invoked.

## Dependencies And Integration Points

The implementation depends on `DefaultEnv`, `Env`, `Log`, `Utils::GetDirectoryEntries`, `Utils::ProcessConfig`, `Utils::splitString`, `URL`, `XrdSysPwd`, `XrdOucPinLoader`, and version symbols from `XrdVersion.hh`. Plugin libraries must export `extern "C" void *XrdClGetPlugIn(const void *arg)` returning a `PlugInFactory*` and accepting the config map pointer.

## Risks And Edge Cases

`ProcessEnvironmentSettings` allocates `pDefaultFactory` even when `LoadFactory` returns a null loader/factory for the `PlugIn` path, so failed default loading can still leave an env default helper with null factory. Programmatic registration cannot override environment plugins. Counter management is manual; incorrect sharing/removal can leak or double-delete factories. Config docs mention `enabled`, while code requires `enable`. `NormalizeURL` rejects invalid URL strings and collapses wildcard hostnames to protocol-only keys.

## Test Signals

Tests should cover exact URL, wildcard host/protocol, and default precedence; disabling config entries; multiple URLs sharing one factory; failed library load; invalid config keys; programmatic override rejection for env entries; and destructor cleanup. Integration tests should load a minimal shared plugin exporting `XrdClGetPlugIn`.
