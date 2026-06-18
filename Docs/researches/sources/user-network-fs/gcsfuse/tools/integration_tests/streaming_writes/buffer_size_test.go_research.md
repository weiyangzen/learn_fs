# sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/buffer_size_test.go

## Purpose

Tests streaming-write behavior under different write buffer configurations by mounting a separate gcsfuse instance and writing files whose sizes are smaller than, equal to, or larger than the configured block pool capacity.

## Important APIs, control flow, and dependencies

`TestWritesWithDifferentConfig` skips mounted-directory mode, creates a private mount directory, temporarily swaps `testEnv.cfg.GCSFuseMountedDirectory`, and runs subtests with `static_mounting.MountGcsfuseWithStaticMountingWithConfigFile`. Cases vary `--write-block-size-mb` and `--write-max-blocks-per-file`, then create a local file, generate data with `operations.GenerateRandomData`, write through `operations.WriteAt`, and validate close-time upload through `CloseFileAndValidateContentFromGCS`.

## State, persistence, dependencies, and integration points

The test manipulates package config state and restores it with `defer`. Each subtest mounts and unmounts independently, creates a fresh test directory, and validates the object lifecycle differs for zonal buckets, where file creation may create an empty object earlier, versus non-zonal buckets, where the object is not expected until upload.

## Risks and test signals

Risks include global config mutation, resource leaks from nested mounts, and boundary bugs when `blockSize * maxBlocks` is less than file size. Signals are successful stateless remount, correct pre-upload object state, and exact GCS content after closing the file for all buffer-size combinations.
