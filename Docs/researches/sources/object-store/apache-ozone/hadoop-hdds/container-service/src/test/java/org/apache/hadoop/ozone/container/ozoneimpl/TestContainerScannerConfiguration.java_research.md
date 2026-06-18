# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestContainerScannerConfiguration.java

## Purpose
This suite verifies configuration binding and validation for `ContainerScannerConfiguration`, including metadata scan interval, data scan interval, minimum per-container scan gap, background bandwidth, and on-demand bandwidth.

## Important APIs, types, and functions
The tests use `OzoneConfiguration`, `conf.getObject(ContainerScannerConfiguration.class)`, scanner configuration keys, defaults, and `StorageUnit.MB.toBytes`.

## Control flow
`acceptsValidValues` sets positive interval and bandwidth values and expects getters to return them unchanged. `overridesInvalidValues` sets negative intervals and bandwidths and expects defaults. `isCreatedWitDefaultValues` builds the object from an empty configuration and expects scanning enabled with all default values.

## State and persistence behavior
No filesystem state is used. The state under test is the configuration object generated from `OzoneConfiguration` and its validation/defaulting logic.

## Dependencies and integration points
The tested configuration feeds background data scanners, metadata scanners, and on-demand scanner throttling. Correct validation prevents disabled or nonsensical scanner scheduling due to bad configuration.

## Risks and edge cases
Risks include accepting negative intervals or bandwidths, overriding valid values, defaulting on-demand bandwidth incorrectly, and accidentally disabling scanning by default.

## Test signals
Signals are exact getter values for valid inputs, exact default constants for invalid inputs, and `isEnabled()` being true for default configuration.
