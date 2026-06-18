<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/OzoneTenant.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/OzoneTenant.java

## Purpose

`OzoneTenant` is an in-memory representation of a tenant, including tenant ID, role names, access policies, account namespace, and bucket namespace.

## Important APIs, Types, And Functions

It implements `Tenant` and exposes tenant name, account namespace, bucket namespace, access policy list, role list, mutators for policies and roles, and `toString`.

## Control Flow, State, And Persistence

Construction creates an `AccountNameSpaceImpl` and `SingleVolumeTenantNamespace` with the tenant ID. Policy and role lists are mutable `ArrayList`s. The class comment points to DB state elsewhere (`OmDBTenantState`); this object is not the authoritative persisted record.

## Dependencies And Integration Points

It depends on `Tenant`, `AccountNameSpaceImpl`, and `SingleVolumeTenantNamespace`. It integrates with tenant-management logic and Ranger role/policy setup.

## Risks And Test Signals

Getters expose mutable lists directly, so external callers can alter tenant state. Tests should cover add/remove role and policy behavior, namespace IDs, default single-volume namespace mapping, and consistency with persisted tenant DB state.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/OzoneTenant.java -->
