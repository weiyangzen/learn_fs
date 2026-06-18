# sources/object-store/apache-ozone/hadoop-ozone/client/pom.xml

## Purpose
Build-support SpotBugs/FindBugs exclusion file that suppresses selected static-analysis findings for the Ozone client module. This research is based on a complete read of the 149-line source file.

## Important APIs and Types
Artifact/build declarations include `hdds-hadoop-dependency-client`, `ozone-client`, `jackson-annotations`, `jcip-annotations`, `guava`, `jakarta.annotation-api`, `commons-collections4`, `commons-lang3`, `hadoop-common`, `hdds-client`, `hdds-common`, `hdds-config`, `hdds-erasurecode`, `hdds-interface-client`, `ozone-common`, `ozone-interface-client`, `ratis-common`, `ratis-thirdparty-misc`.

## Control Flow
No runtime control flow. The XML is consumed by static-analysis tooling during Maven/QA runs to filter known findings.

## State and Persistence
Persists static-analysis policy in source control only; it does not affect runtime server state.

## Dependencies and Integration Points
This descriptor feeds Maven reactor builds and publishes the `ozone-client` module consumed by CLI and application code.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
No direct test file is paired in this item; validation should include command parser tests and mocked ObjectStore/OzoneBucket interaction tests.
