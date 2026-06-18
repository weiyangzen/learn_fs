# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPlugin.cc

## Purpose

This file exposes the C ABI entry points used when the xroot protocol is loaded as an ancillary shared-library protocol. It constructs the protocol object and reports the protocol port to the hosting XRootD protocol driver.

## Important APIs, types, and functions

`XrdgetProtocol()` logs the startup banner, calls `XrdXrootdProtocol::Configure(parms, pi)`, and returns a new `XrdXrootdProtocol` on success. `XrdgetProtocolPort()` returns `pi->Port` when configured or the default xroot port `1094`. `XrdVERSIONINFO` annotates both exported entry points.

## Control flow

The host loads the shared object, calls `XrdgetProtocolPort()` early, then calls `XrdgetProtocol()`. Configuration failure returns null and logs initialization as failed; success returns an unbound prototype protocol instance whose `Match()` method later recognizes and binds xroot links.

## State and persistence behavior

This file stores no state. It delegates all configuration and static process state setup to `XrdXrootdProtocol::Configure()`.

## Dependencies and integration points

It depends on `XrdVersion.hh` and `XrdXrootdProtocol.hh`. A near-identical loader is also present in `XrdXrootdProtocol.cc` for builds where the protocol is not ancillary; build configuration must avoid duplicate exported definitions in the same link unit.

## Risks and edge cases

The default port behavior assumes one xroot port per protocol instance. Errors from `Configure()` are reduced to a null return and log text, so detailed diagnostics must come from configuration code. ABI compatibility depends on the exported names and version metadata remaining stable.

## Test signals

Integration tests should load the plugin through the XRootD protocol manager, verify default and configured port selection, and assert failed configuration returns null without leaving partially initialized protocol state usable.
