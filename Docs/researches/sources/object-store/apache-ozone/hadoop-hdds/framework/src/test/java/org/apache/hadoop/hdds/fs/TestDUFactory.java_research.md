# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDUFactory.java

## Purpose

This class validates that `DUFactory` can be selected through configuration and creates expected `SpaceUsageCheckParams`.

## Important APIs, Types, And Functions

`testCreateViaConfig()` delegates to `TestSpaceUsageFactory.testCreateViaConfig(DUFactory.class)`. `testParams()` uses `DUFactory.Conf`, `setRefreshPeriod`, `conf.setFromObject`, `new DUFactory().setConfiguration(conf).paramsFor(dir)`, and assertions over params.

## Control Flow

The test writes a one-hour refresh period into `OzoneConfiguration`, creates a factory, asks for params for a temp directory, and checks the source and persistence classes.

## State And Persistence

State is in-memory configuration and a temp directory reference. The params use `SaveSpaceUsageToFile`, but this test does not write the file.

## Dependencies And Integration Points

It integrates `DUFactory`, config object binding, `SpaceUsageCheckFactory.create`, `DU`, and `SaveSpaceUsageToFile`.

## Risks

The test checks exact runtime classes, so subclassing or decorator changes will need intentional updates. It does not validate the path or expiry details of `SaveSpaceUsageToFile`.

## Test Signals

Signals include configured factory class selection, correct directory identity, exact refresh duration, `DU` source class, and `SaveSpaceUsageToFile` persistence class.
