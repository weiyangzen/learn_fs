# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsUtils.cc

## Purpose

`XrdCmsUtils.cc` implements CMS utility functions for loading performance-monitor plugins, parsing manager host/port/site specifications, displaying resolved manager addresses, and mapping site numbers to names.

## Important APIs and Functions

`loadPerfMon()` pins a plugin with `XrdOucPinLoader` and resolves `XrdCmsPerfMonitor`. `ParseMan()` parses manager host specifications, optional `@site` tags, optional `%instance` scope, trailing `+` address expansion, numeric or service-name ports, dynamic DNS behavior, duplicate suppression, and sorted insertion into an `XrdOucTList`. `ParseManPort()` extracts a port from `host:port` syntax or the next config token. `SiteName()` returns a registered site name or `anonymous`. Private `Display()` logs DNS-to-address mappings and `SInsert()` inserts managers in a deterministic order.

## Control Flow

`ParseMan()` first lazily initializes `siteList` from `XRDSITE` or `local`, then strips site and instance qualifiers from `hPort`. It detects trailing `+` in `hSpec` for multi-address expansion, rejects hostname globbing with dynamic DNS, resolves/validates the port, resolves hosts unless dynamic DNS defers resolution, optionally updates `sPort` for local-address matches, and merges non-duplicates into the existing list.

## State and Persistence Behavior

The file maintains static `siteList` and `siteIndex` for process-lifetime site IDs. It mutates input strings in place by replacing delimiters such as `@`, `%`, `+`, and `:` with NUL bytes. Returned manager lists and port strings are caller-owned. Plugin loading pins shared libraries for process lifetime.

## Dependencies and Integration Points

Dependencies include `XrdNetAddr`, `XrdNetUtils`, `XrdOuca2x`, `XrdOucPinLoader`, `XrdOucStream`, `XrdOucTList`, and `XrdSysError`. The functions are called by CMS configuration parsing and performance-monitor setup.

## Risks and Edge Cases

Callers must pass mutable buffers; passing string literals would be unsafe. `SInsert()` sorts with a non-obvious condition and should be tested for intended host/port ordering. Static site state is not synchronized, so concurrent configuration parsing could race. Dynamic DNS mode stores unresolved hostnames and changes duplicate/local-port semantics.

## Test Signals

Tests should cover numeric and service ports, IPv6 bracket parsing, missing port errors, `@site` registration, `%instance` filtering against `XRDNAME`, trailing `+` multi-host expansion, dynamic DNS paths, duplicate manager warnings, and `SiteName()` fallback.
