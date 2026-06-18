<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmTenantUserArgs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmTenantUserArgs.java

## Purpose

`OmTenantUserArgs` is a small request DTO for tenant-user operations. The source comment notes it is currently unused.

## Important APIs, Types, And Functions

The constructor stores `tenantUsername` and `tenantId`; getters return those fields.

## Control Flow, State, And Persistence

It is immutable after construction and contains no serialization or persistence hooks. If adopted by a request path, persistence would occur in OM tenant access-id tables.

## Dependencies And Integration Points

The class has no external dependencies beyond Java `String`. It is in the helpers package near active tenant DTOs such as `OmTenantArgs`, `TenantUserInfoValue`, and `TenantUserList`.

## Risks And Test Signals

There is no validation or null checking. If this type is wired into a live API, tests should cover null principal, null tenant, invalid principal syntax, and conversion to any corresponding protobuf request.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmTenantUserArgs.java -->
