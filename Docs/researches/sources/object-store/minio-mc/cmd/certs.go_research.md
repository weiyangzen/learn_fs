# sources/object-store/minio-mc/cmd/certs.go

## Purpose

`certs.go` manages MinIO Client certificate and CA directory paths and loads trusted root CAs.

## Important APIs, Types, and Functions

Functions include `getCertsDir`, `isCertsDirExists`, `createCertsDir`, `getCAsDir`, `mustGetCAsDir`, `isCAsDirExists`, `createCAsDir`, and `loadRootCAs`.

## Control Flow

Path helpers derive `certs` and `CAs` directories from the mc config directory. Existence helpers call `os.Stat`. Creation helpers use `os.MkdirAll` with mode `0700`. `loadRootCAs` calls `certs.GetRootCAs` with the CAs directory and stores the result in `globalRootCAs`.

## State and Persistence Behavior

The file creates local certificate directories and updates in-memory `globalRootCAs`. CA files themselves are read by the certs package.

## Dependencies and Integration Points

It depends on config directory helpers, global constants `globalMCCertsDir` and `globalMCCAsDir`, `github.com/minio/pkg/v3/certs`, and `fatalIf`.

## Risks and Edge Cases

`is*Exists` treats all `os.Stat` errors as non-existence. `mustGetCAsDir` suppresses errors by returning an empty string, so callers must tolerate that. Directory permissions are restrictive by design.

## Test Signals

Tests should cover path construction, create permissions, stat error behavior, missing config directory errors, and CA load failure handling.
