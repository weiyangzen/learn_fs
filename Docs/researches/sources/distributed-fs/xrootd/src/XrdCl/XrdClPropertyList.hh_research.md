# sources/distributed-fs/xrootd/src/XrdCl/XrdClPropertyList.hh

## Purpose

This header implements `PropertyList`, a small string-backed key/value container with templated typed set/get helpers and specializations for XrdCl status, URL, and string-vector values.

## Important APIs, Types, And Functions

`PropertyList::Set(name, value)` streams arbitrary values into strings. `Get(name, item)` streams strings back into an output item and returns whether a key/conversion exists. `Get<Item>(name)` returns the converted value or `Item()`. Indexed overloads store keys as `"name index"`. `HasProperty`, iterators, and `Clear` expose map operations.

Specializations preserve full strings without stream tokenization, serialize `XRootDStatus` as `status;code;errNo#errorMessage`, serialize `URL` as `URL::GetURL()`, and serialize `std::vector<std::string>` as numbered repeated properties.

## Control Flow

Setters update `pProperties`. Generic getters locate the key, stream into the requested type, and fail only on `bad()`. Vector get loops from index zero until the indexed property is missing, appending values in order.

## State And Persistence Behavior

State is an in-memory `std::map<std::string, std::string>`. There is no built-in persistence, but the string map can be iterated for external serialization.

## Dependencies And Integration Points

The header includes `XrdClXRootDResponses.hh`, which supplies `XRootDStatus` and `URL` dependencies. Property lists are a common utility for passing structured metadata through APIs that need generic string properties.

## Risks And Edge Cases

Generic conversion checks `i.bad()` but not `fail()`, so malformed input may be accepted with default/partial values. Indexed keys use spaces despite the `name must not contain spaces` comment, so callers must avoid ambiguous names. Vector serialization does not store a length; missing middle indices truncate reads. `XRootDStatus` serialization uses `#` and semicolons as separators and assumes status message handling remains compatible.

## Test Signals

Tests should cover string values containing spaces, numeric conversion failures, indexed properties, vector round trips with missing middle entries, status error-message preservation, URL parsing, iteration order, and `Clear`.
