# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/HDDSVolumeLayoutVersion.java

## Purpose
Small registry of datanode volume layout versions.

## Important APIs, Types, And Functions
Static APIs `getAllVersions` and `getLatestVersion`; instance getters expose version number and description. The current array contains version 1.

## Control Flow
Callers read all known volume layout versions or the latest entry; ordering of the private array determines latest.

## State And Persistence
Immutable objects in a private static array; arrays returned to callers are clones.

## Dependencies And Integration Points
Related to datanode volume formatting and storage metadata code.

## Risks
Future version additions must append in order. The class is separate from datanode metadata layout versions and can be confused with `HDDSLayoutFeature`.

## Test Signals
Signals include latest version selection, cloned array immutability, and storage code using the expected volume layout number.
