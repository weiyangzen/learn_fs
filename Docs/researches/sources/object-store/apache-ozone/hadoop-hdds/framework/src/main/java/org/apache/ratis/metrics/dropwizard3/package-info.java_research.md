# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/ratis/metrics/dropwizard3/package-info.java

## Purpose
This package descriptor documents `org.apache.ratis.metrics.dropwizard3` as the utility package for Ratis Dropwizard3 metrics integration.

## Important APIs, Types, And Functions
The only declaration is the package statement. The principal local API in this package is `RatisMetricsUtils`, which bridges Ratis metric registries to Dropwizard and JMX reporting helpers.

## Control Flow
There is no runtime control flow.

## State And Persistence
No state is stored and no persistence occurs.

## Dependencies And Integration Points
The file integrates with Java package documentation for the Dropwizard3 Ratis metrics bridge used by Ozone HTTP metrics export.

## Risks
The descriptor can become stale if the package grows beyond utility classes or changes responsibility. There are no executable risks.

## Test Signals
Compilation and Javadoc generation are sufficient. Behavioral coverage belongs to `RatisMetricsUtils` and `RatisDropwizardExports` tests.
