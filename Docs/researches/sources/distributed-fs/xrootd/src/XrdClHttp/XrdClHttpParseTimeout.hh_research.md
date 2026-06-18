# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpParseTimeout.hh

## Purpose

This header declares the timeout duration parser and formatter used by the XrdCl HTTP plugin configuration layer.

## Important APIs, types, and functions

`ParseTimeout(const std::string&, struct timespec&, std::string&)` returns a success flag and writes a diagnostic error message on invalid input. `MarshalDuration(const struct timespec&)` returns a Go-style duration string with seconds and milliseconds.

## Control flow

Callers pass configuration strings into `ParseTimeout` before updating static timeout settings. On false, they log `errmsg` and typically keep defaults. `MarshalDuration` is used for converting a stored `timespec` back to display/config text.

## State and persistence behavior

The header declares stateless functions only. Parsed state belongs to callers.

## Dependencies and integration points

It includes `<time.h>` for `timespec` and `<string>`. `XrdClHttpFactory.cc` and `XrdClHttpFile.cc` include it for environment/property parsing.

## Risks and edge cases

Consumers must handle a false parse and should not assume `result` was changed meaningfully on failure. The documented format excludes the UTF-8 microsecond symbol even though Go accepts it.

## Test signals

Compile coverage is broad because factory/file code includes this header. Behavioral tests should target the `.cc` parser.
