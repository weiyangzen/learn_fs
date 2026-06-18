# sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/main/java/org/apache/hadoop/ozone/iceberg/package-info.java

## Purpose
This package descriptor documents Apache Ozone integration with Apache Iceberg.

## Important APIs, types, and functions
The package contains the CLI root command, rewrite-path subcommand, Ozone rewrite action, and helper utilities.

## Control flow
No executable behavior is present in the descriptor.

## State and persistence behavior
No package-level state exists.

## Dependencies and integration points
The package bridges Ozone CLI/configuration with Iceberg table metadata and file IO.

## Risks and edge cases
Package-level compatibility depends on Iceberg APIs and Ozone filesystem dependencies declared by the module POM.

## Test signals
Compilation and `TestRewriteTablePathOzoneAction` validate the package.
