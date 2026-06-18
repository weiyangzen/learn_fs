# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdRedirPI.hh

## Purpose

This header defines the redirect plugin interface for xrootd. A plugin can rewrite redirect targets based on original target address, client address, port, CGI data, and URL components.

## Important APIs, types, and functions

`Redirect()` is the required host-form method. `RedirectURL()` is optional and defaults to no rewrite. `XrdXrootdRedirPI_Args` and `XrdXrootdRedirPI_t` define the C factory signature `XrdXrootGetdRedirPI()`, including previous plugin pointer, logger, parameters, config path, and environment.

## Control flow

The server loads a shared plugin, calls its factory, and passes the resulting object to `XrdXrootdRedirHelper`. For each redirect, the helper calls `Redirect()` or `RedirectURL()`. A non-empty reply replaces the target; an empty reply keeps the original; a reply beginning with `!` reports a fatal error message to the client.

## State and persistence behavior

The interface owns no state. Concrete plugins may keep configuration or caches; ownership is external to this header.

## Dependencies and integration points

It depends on C++ `std::string`, `uint16_t`, and forward-declared XRootD network/logger/environment types. It integrates with plugin loading, compatibility checks via `XrdVERSIONINFO`, and the redirect helper.

## Risks and edge cases

Plugin authors must include CGI data in replacement host targets when needed. `RedirectURL()` should not change the original protocol. The factory comment mistakenly says "file system object" in its return description, but the typedef correctly returns `XrdXrootdRedirPI *`.

## Test signals

Tests belong mostly to helper/plugin integration: factory loading, chaining via `prevPI`, reply-string interpretation, URL default no-op behavior, and compatibility metadata enforcement.
