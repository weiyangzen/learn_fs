# sources/user-network-fs/rclone/cmd/serve/dlna/data/data.go

## Purpose

`data.go` provides runtime access to the embedded DLNA root device descriptor template.

## Important APIs, Types, and Functions

`GetTemplate` opens `rootDesc.xml.tmpl` from `Assets`, reads it fully, parses it as a `text/template`, and returns the parsed template.

## Control Flow

The function reports wrapped errors for open, read, and parse failures. It uses `fs.CheckClose` to close the embedded file while preserving an existing error.

## State and Persistence Behavior

No persistent state is written. Each call parses a fresh template rather than caching it.

## Dependencies and Integration Points

`server.rootDescHandler` calls `GetTemplate` per request to render root device XML using server fields and service descriptors.

## Risks and Test Signals

Repeated parsing is simple but adds per-request work. Template errors would break discovery. `dlna_test.go` checks that root SCPD output includes expected services and URLs.
