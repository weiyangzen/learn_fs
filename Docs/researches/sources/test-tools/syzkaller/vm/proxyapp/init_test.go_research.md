# sources/test-tools/syzkaller/vm/proxyapp/init_test.go

## Purpose

`init_test.go` verifies proxyapp configuration parsing and URI validation.

## Important APIs, Types, and Functions

Tests are `TestParseConfig` and `TestURIParseErr`. They use `parseConfig`, `URIParseErr`, `Config`, and `testify/assert`.

## Control Flow

The parse-config table checks command plus URI, command-only, URI-only, missing both, valid and invalid URI shapes, and optional remote plugin config. The URI test directly checks accepted host:port forms and rejected scheme/no-port inputs.

## State and Persistence Behavior

The tests are in-memory only.

## Dependencies and Integration Points

They protect the config contract consumed by `proxyappclient.ctor`.

## Risks and Test Signals

They do not exercise TLS setup, subprocess launch, reconnection, or RPC calls. Strong signals are rejecting empty plugin configuration and preserving `json.RawMessage` plugin config without semantic interpretation.
