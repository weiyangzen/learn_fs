# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsTypes.hh

## Purpose

`XrdCmsTypes.hh` defines shared CMS constants and scalar types used across the CMS manager, server, and redirector code.

## Important APIs and Types

`SMask_t` is an unsigned 64-bit mask type with `FULLMASK` set to all bits. `STMax` sets the maximum subscriber cell size to 64. `maxRD` is 65, one greater than the real maximum redirector count because slot zero is unused. `XrdCmsMAX_PATH_LEN` is 1024 and `XrdCmsVERSION` is `1.0.0`.

## Control Flow

There is no executable control flow; the header provides compile-time constants.

## State and Persistence Behavior

There is no runtime state. The constants shape in-memory masks, array sizes, path buffers, and version reporting elsewhere.

## Dependencies and Integration Points

Many CMS headers and implementations include this file to agree on mask width, subscriber limits, redirector slots, and path-length assumptions.

## Risks and Edge Cases

The 64-bit mask and `STMax` must stay aligned; increasing subscriber counts without changing mask representation would break bitset logic. Fixed path length may truncate or reject longer admin/config paths depending on consumers.

## Test Signals

Compile-time/static tests should assert `STMax <= sizeof(SMask_t) * 8` and redirector arrays account for unused slot zero.
