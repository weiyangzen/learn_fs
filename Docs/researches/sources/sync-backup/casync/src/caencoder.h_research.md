# sources/sync-backup/casync/src/caencoder.h

## Purpose
Declares the opaque `CaEncoder` API used to turn filesystem input into a casync archive stream. It is the public contract for encoder setup, stepping, data retrieval, metadata inspection, seek/resume, and digest reporting.

## Important APIs, Types, and Functions
`CaEncoder` is opaque. Step result constants distinguish stream completion, file boundaries, payload availability, and generic data availability. Setup functions configure feature flags, UID shift/range, and the base fd. `ca_encoder_step` drives the state machine; `ca_encoder_get_data` returns archive bytes. Current metadata accessors expose path, mode, target, mtime, size, uid/gid/name/group, device, chattr/FAT flags, xattrs, quota project ID, offsets, and `CaLocation`. Digest controls enable and retrieve archive, payload, and hardlink digests.

## Control Flow
Callers create an encoder, set feature flags/base fd, repeatedly call `ca_encoder_step`, and fetch data when the step result indicates payload or archive data. Metadata accessors are valid around current-file states. `ca_encoder_seek_location` repositions the stream to a prior `CaLocation`.

## State and Persistence Behavior
The header exposes no structure fields, but the API preserves offsets and locations across streaming and allows digest state to be queried only at specific lifecycle points. The base fd remains owned externally but is used as the root for traversal.

## Dependencies and Integration Points
Includes `cachunkid.h`, `cacommon.h`, and `calocation.h`. Used by casync synchronization and archiving layers that need source-tree serialization and resumable addressing.

## Risks
The API is order-dependent: calling data, metadata, digest, or seek functions in the wrong state returns errors. Consumers must respect ownership of returned pointers and only rely on digest values after complete relevant reads.

## Test Signals
Compile-time ABI coverage, null-argument/error-state checks, step/data loop integration, location seek round trips, and digest enable/disable behavior are the key signals.
