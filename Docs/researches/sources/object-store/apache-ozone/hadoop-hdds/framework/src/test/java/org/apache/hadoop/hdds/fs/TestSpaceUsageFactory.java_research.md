# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestSpaceUsageFactory.java

## Purpose

This class tests `SpaceUsageCheckFactory.create(ConfigurationSource)` selection, configuration injection, and fallback behavior for broken or invalid factory class settings.

## Important APIs, Types, And Functions

Important helpers are `testCreateViaConfig`, `configFor`, `assertCreatesDefaultImplementation`, `testDefaultFactoryForBrokenImplementation`, and `testDefaultFactoryForWrongConfig`. Nested classes model broken implementations and a configurable `SpyFactory`.

## Control Flow

Tests populate `configKeyForClassName()` with valid, missing, private, empty, unknown, and non-implementing class values. Factory creation is invoked, then the class, configuration injection, default fallback, and log output are asserted.

## State And Persistence

State is in-memory configuration and captured logs via `LogCapturer`. There is no filesystem persistence.

## Dependencies And Integration Points

The class integrates with `OzoneConfiguration`, `ConfigurationSource`, `SpaceUsageCheckFactory`, logging, reflection-based class loading, and concrete factory tests that reuse `testCreateViaConfig`.

## Risks

The tests depend on log-message inclusion for invalid nonempty config values. They do not call `paramsFor` on successful real factories except through other test classes.

## Test Signals

Signals include correct factory instantiation for valid config, `setConfiguration` being called, default fallback for unusable classes or bad config, no log for empty config, and log mentioning invalid configured class names.
