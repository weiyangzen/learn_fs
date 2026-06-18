# sources/user-network-fs/rclone/cmd/serve/dlna/data/assets_generate.go

## Purpose

This ignored generator embeds DLNA static assets into Go source.

## Important APIs, Types, and Functions

`main` uses `vfsgen.Generate` over `http.Dir("./static")`, package name `data`, build tag `!dev`, and variable name `Assets`.

## Control Flow

`go generate` runs this program from the data directory. It scans `static`, generates `assets_vfsdata.go`, and exits fatally on generator errors.

## State and Persistence Behavior

It writes generated Go source during developer generation, not at runtime.

## Dependencies and Integration Points

It depends on `github.com/shurcooL/vfsgen`, the `static` asset directory, and `data.go` which opens `Assets`.

## Risks and Test Signals

Risks are stale generated assets when XML/templates/images change, and mismatch between `dev` and non-`dev` builds. There is no direct generator test; compile-time use of `data.Assets` and root descriptor tests provide indirect coverage.
