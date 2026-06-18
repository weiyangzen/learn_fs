# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDUOptimizedFactory.java

## Purpose

This class tests that `DUOptimizedFactory` creates params using the optimized disk-usage source, configured refresh period, and file persistence.

## Important APIs, Types, And Functions

The test uses `DUFactory.Conf`, `OzoneConfiguration`, `DUOptimizedFactory.setConfiguration`, and `paramsFor(File, Supplier<File>)`. It asserts `SpaceUsageCheckParams` contents.

## Control Flow

The test writes a 30-minute refresh into configuration, creates the factory, supplies an exclusion file provider, and obtains params for a temp directory.

## State And Persistence

Only configuration and temp path references are held. The resulting persistence class is `SaveSpaceUsageToFile`, but no actual save/load occurs.

## Dependencies And Integration Points

It integrates with `DUOptimizedFactory`, shared `DUFactory.Conf`, `DUOptimized`, and `SaveSpaceUsageToFile`.

## Risks

The test confirms class wiring but not whether the exclusion provider is later honored by `DUOptimized`. Exact-class assertions may need updates for wrapper implementations.

## Test Signals

Signals are correct directory identity, refresh duration, `DUOptimized` source class, and `SaveSpaceUsageToFile` persistence class.
