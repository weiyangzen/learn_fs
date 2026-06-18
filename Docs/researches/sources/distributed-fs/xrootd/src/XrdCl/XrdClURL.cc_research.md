# sources/distributed-fs/xrootd/src/XrdCl/XrdClURL.cc

## Purpose

This file implements XrdCl URL parsing, normalization, reconstruction, and query-parameter helpers. It supports root/xroot URLs, local file shorthand, stdio `-`, HTTP/DAV default ports, IPv6 bracket handling, metalink detection, secure protocol detection, TPC intent detection, and auth obfuscation.

## Important APIs, Types, and Functions

Constructors call `FromString`. Parsing is split across `FromString`, `ParseHostInfo`, `ParsePath`, and `SetParams`. Derived views include `GetPathWithParams`, `GetPathWithFilteredParams`, `GetLocation`, `GetParamsAsString`, `GetLoginToken`, `GetObfuscatedURL`, and `GetChannelId`. State recomputation uses `ComputeHostId`, `ComputeURL`, and `Clear`. Classification helpers include `IsValid`, `IsMetalink`, `IsLocalFile`, `IsSecure`, `IsTPC`, and `PathEndsWith`.

## Control Flow

`FromString` clears state, selects protocol from `://`, absolute path, `-`, or root default, adjusts default ports for HTTP/DAV, splits host info and path according to protocol, parses host/user/password/port, parses path/query, rebuilds `pURL`, and logs details with optional auth obfuscation. `ParseHostInfo` handles user/password before `@`, IPv6 bracket addresses, IPv6-encoded IPv4 simplification, and numeric port validation. `SetParams` splits opaque info on `&`, supports values with `=`, and extracts login tokens after an embedded `?`.

## State and Persistence Behavior

URL objects store parsed components and a reconstructed URL string. Setters mutate components and recompute dependent fields immediately. There is no persistence.

## Dependencies and Integration Points

It depends on XrdCl logging/default environment/constants/utils/optimizers, XrdOuc utility headers, and metalink environment configuration. Copy, stream, transport, and checksum code consume URL channel IDs, filtered params, security flags, and TPC intent.

## Risks and Edge Cases

The parser is intentionally simple and does not perform general URL escaping/decoding. Query params are stored in `std::map`, so original order and duplicate keys are lost. `GetParamsAsString(true)` can produce an extra ampersand after filtering earlier keys because separator logic uses the original iterator position. `ComputeURL` sets `pURL` empty for invalid state but continues building afterward. Passwords can appear in `pHostId`; callers must use obfuscated accessors for logs.

## Test Signals

Tests should cover root default URLs, absolute local paths, stdio, file trailing slash removal, HTTP/DAV ports, IPv6 and IPv6-mapped IPv4, invalid ports/empty hosts, query filtering, login token extraction, channel ID CGI selection, metalink suffix toggled by env, secure protocol flags, and auth obfuscation.
