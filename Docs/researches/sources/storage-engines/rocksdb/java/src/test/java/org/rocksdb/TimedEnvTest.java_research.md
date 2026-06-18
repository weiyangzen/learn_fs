# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/TimedEnvTest.java

## Purpose

This file tests construction and basic DB integration for the Java `TimedEnv` wrapper.

## Important APIs and types

It uses `TimedEnv`, `Env.getDefault`, `Options.setEnv`, `RocksDB.open`, and `RocksDB.put`.

## Control flow

One test constructs and closes a `TimedEnv`. The integration test installs it into options, opens a temporary DB, and writes one key/value pair.

## State and persistence behavior

The environment wraps the default filesystem environment and may collect timing internally, though this file does not inspect metrics. The DB write persists to the temporary folder.

## Dependencies and integration points

This is a smoke test for native env wrapping, option ownership, and DB file operations through a timed environment.

## Risks and test signals

Risks include wrapper construction failure, incorrect delegation to the base env, and native ownership issues. The signal is successful construction, DB open, and write without exception.
