# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/dev-support/findbugsExcludeFile.xml

## Purpose

This SpotBugs filter suppresses one static-analysis warning for the S3 integration-test module.

## Important rules

The filter matches `org.apache.hadoop.ozone.s3.awssdk.v2.AbstractS3SDKV2Tests$S3BucketOwnershipVerificationConditionsTests` and suppresses the `SIC_INNER_SHOULD_BE_STATIC` pattern.

## Control flow, state, and persistence

The XML has no runtime control flow. It is consumed by the module's SpotBugs Maven plugin configuration and affects static-analysis reporting during builds.

## Dependencies and integration points

The file is referenced by `integration-test-s3/pom.xml` as `${basedir}/dev-support/findbugsExcludeFile.xml`. It exists because the nested test class is intentionally non-static or cannot be made static without disrupting test access to enclosing test state.

## Risks and test signals

The risk is that the suppression can hide a real retention or lifecycle issue if the nested class starts holding heavier outer state. The positive build signal is a SpotBugs run that remains focused on actionable warnings while allowing this specific JUnit nested-test structure.
