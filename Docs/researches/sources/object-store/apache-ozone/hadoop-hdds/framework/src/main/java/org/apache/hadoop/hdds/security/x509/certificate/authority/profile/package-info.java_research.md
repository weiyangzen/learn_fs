# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/profile/package-info.java

## Purpose

This package descriptor documents Ozone certificate authority profile classes and describes PKI profiles as executable certificate policy.

## Important APIs, Types, and Functions

No executable APIs are present. The package contains `PKIProfile`, `DefaultProfile`, and `DefaultCAProfile`.

## Control Flow

No runtime control flow.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

The package integrates BouncyCastle X.509 policy primitives with the SCM CA approver.

## Risks and Edge Cases

The package text can drift from implemented profile behavior.

## Test Signals

Compile and JavaDoc generation are sufficient.
