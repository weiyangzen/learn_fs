<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/TenantUserInfoValue.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/TenantUserInfoValue.java

## Purpose

`TenantUserInfoValue` wraps the access IDs associated with one user across tenants for tenant user-info responses.

## Important APIs, Types, And Functions

It stores a `List<ExtendedUserAccessIdInfo>`, exposes `getAccessIdInfoList`, static `fromProtobuf(TenantGetUserInfoResponse)`, `getProtobuf`, `toString`, `equals`, and `hashCode`.

## Control Flow, State, And Persistence

The class is a protocol response wrapper. `fromProtobuf` takes the repeated list from a response; `getProtobuf` builds a new `TenantGetUserInfoResponse` and adds each access-id info entry. Persistence is handled by OM tenant/access-id DB tables.

## Dependencies And Integration Points

It depends on tenant user-info protobuf messages. It integrates with `OzoneManagerProtocol.tenantGetUserInfo`, tenant administration CLI output, and S3 access-id management.

## Risks And Test Signals

The list is stored and returned directly. Tests should cover empty users, multiple access IDs, admin/delegated admin flags inside entries, protobuf round trips, and mutation expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/TenantUserInfoValue.java -->
