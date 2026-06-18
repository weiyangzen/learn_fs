<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/OzoneTenantRolePrincipal.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/OzoneTenantRolePrincipal.java

## Purpose

`OzoneTenantRolePrincipal` is a Java `Principal` wrapper for a tenant Ranger role name.

## Important APIs, Types, And Functions

It stores `tenantRoleName`, implements `getName`, and returns the name from `toString`.

## Control Flow, State, And Persistence

The object is immutable and carries no persistence behavior. It is used as a principal identity in authorization or policy construction.

## Dependencies And Integration Points

It depends on `java.security.Principal` and integrates with Ozone multitenancy and Ranger role assignment code.

## Risks And Test Signals

There is no null or format validation. Tests should cover exact name propagation, string conversion, and policy code behavior for invalid or missing role names.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/OzoneTenantRolePrincipal.java -->
