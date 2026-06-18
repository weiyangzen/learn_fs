<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/TenantUserList.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/TenantUserList.java

## Purpose

`TenantUserList` wraps the list of user principal to access ID pairs for users assigned to a tenant.

## Important APIs, Types, And Functions

It exposes the constructor, `getUserAccessIds`, static `fromProtobuf(TenantListUserResponse)`, `toString`, `equals`, and `hashCode`.

## Control Flow, State, And Persistence

The class is a transient response object for tenant listing. It stores the protobuf repeated field directly. It does not provide a reverse `getProtobuf`; translators build list responses elsewhere.

## Dependencies And Integration Points

It depends on `TenantListUserResponse` and `UserAccessIdInfo` protobufs. It integrates with `OzoneManagerProtocol.listUsersInTenant` and tenant management clients.

## Risks And Test Signals

Direct list exposure can allow accidental mutation. Tests should cover empty tenant, prefix-filtered results, multiple users/access IDs, equality/hash behavior, and client display ordering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/TenantUserList.java -->
