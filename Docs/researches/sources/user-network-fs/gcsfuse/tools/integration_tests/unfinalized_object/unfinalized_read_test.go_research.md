# sources/user-network-fs/gcsfuse/tools/integration_tests/unfinalized_object/unfinalized_read_test.go

## Purpose

Tests read behavior for unfinalized zonal objects created through the mount or modified remotely. It focuses on O_DIRECT versus non-O_DIRECT reads after remote append, EOF behavior, and content visibility beyond the cached object size.

## Important APIs, control flow, and dependencies

Constants define one MiB initial and append sizes plus read flags. `setupAndAppend` creates an unfinalized object, opens it with requested flags, reads initial content to cache state, appends remotely with `client.AppendableWriter` at the current generation, and verifies generation stability. `TestUnfinalizedObjectsCanBeRead` reads an unfinalized same-mount file through an O_DIRECT readonly handle. `TestReadRemotelyModifiedUnfinalizedObject` table-drives offsets, read sizes, expected byte counts, EOF expectations, and expected content stitching.

## State, persistence, dependencies, and integration points

The key state distinction is cached size versus actual size after append. O_DIRECT reads are expected to bypass or refresh enough state to read appended bytes, including partial ranges crossing the original end; non-O_DIRECT reads beyond cached size currently return EOF. The suite runs under metadata cache and kernel-reader flag variants from config.

## Risks and test signals

Risks include stale cached size, kernel read path differences, wrong EOF semantics, and generation mismatch after append. Signals are exact initial content, preserved generation, byte count and error equality for each subcase, and expected content slices combining original and appended data.
