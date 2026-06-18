# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/validation/testvalidatorset2/ValidatorsForOnlyOldClientValidations.java

## Purpose
This small fixture class supplies a package with only one old-client validation method. It is used by registry tests that need a package lacking cluster-finalization validators.

## Important APIs and Types
It uses `RequestFeatureValidator`, `ValidationCondition.OLDER_CLIENT_REQUESTS`, phase `PRE_PROCESS`, request type `CreateKey`, `OMRequest`, and `ValidationContext`.

## Control Flow and State
The class is `final` with a private constructor and no mutable state. The single static method `oldClientPreProcessCreateKeyValidator2` is annotated as an old-client, pre-process, create-key validator and returns the request unchanged.

## Dependencies and Integration Points
Its purpose is classpath scanning by `ValidatorRegistry`. `TestValidatorRegistry` constructs a registry constrained to this package and verifies that finalization-condition lookups return no validators.

## Risks and Test Signals
Risk is fixture drift: adding more validators to this package would invalidate tests that rely on its narrow scope. The absence of side effects keeps it safe for scanning tests.
