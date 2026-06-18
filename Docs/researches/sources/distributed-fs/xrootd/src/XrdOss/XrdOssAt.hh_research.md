# sources/distributed-fs/xrootd/src/XrdOss/XrdOssAt.hh

## Purpose

`XrdOssAt.hh` declares `XrdOssAt`, an extended helper API for operations relative to an open OSS directory. It complements the path-based `XrdOss` methods with safer online-only relative operations.

## Important APIs, Types, and Functions

The class declares `Opendir`, `OpenRO`, `Remdir`, `Stat`, and `Unlink`, plus option flag `At_dInfo`. It stores a reference to the associated `XrdOss` filesystem as `ossFS`, although current implementation primarily uses the anchor directory object and default OSS concrete types.

## Control Flow

Callers create one `XrdOssAt` for an OSS system, pass an open directory `XrdOssDF`, and operate on relative path names. The header explicitly notes that many `*at()` variants are not implemented, paths must be relative, no name-to-name processing is applied, and only online copies are affected.

## State and Persistence Behavior

The class itself owns no mutable operation state. Persistence effects are the underlying filesystem changes performed by implementation methods.

## Dependencies and Integration Points

It includes `XrdOucEnv.hh` and forward-declares `stat`, `XrdOss`, and `XrdOssDF`. It integrates with consumers that need race-resistant relative directory operations, such as recursive scans or namespace operations already holding a directory handle.

## Risks and Edge Cases

The contract intentionally differs from Unix `*at()` name handling because no N2N translation occurs. Callers expecting remote/tape-backed behavior must use standard OSS methods. The stored `ossFS` reference currently has limited use, so future extension should avoid assuming it has no semantic role.

## Test Signals

Tests should verify relative-only semantics, online-only behavior, interoperability with `XrdOssDir` and `XrdOssFile`, unsupported method expectations, and `At_dInfo` stat augmentation.
