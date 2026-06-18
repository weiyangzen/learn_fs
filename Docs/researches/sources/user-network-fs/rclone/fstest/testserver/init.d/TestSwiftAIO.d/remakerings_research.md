
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSwiftAIO.d/remakerings

Purpose: replacement Swift ring-building script mounted into the SAIO container to add storage policy `Policy-1`.

Important APIs/types/functions: appends `[storage-policy:1]` to `swift.conf` if absent, removes old builder/ring files, creates/rebalances object, container, account, and object-1 rings with six local devices.

Control flow: sequential shell commands using `swift-ring-builder`.

State/persistence: mutates Swift config and ring files inside the container.

Dependencies/integration: mounted by `TestSwiftAIO` and `TestSwiftAIOsegments`; requires Swift tooling in `openstackswift/saio`.

Risks: assumes working directory and device names used by the SAIO image. Any image layout changes can break ring creation.

Test signals: Swift container starts with default and Policy-1 rings available.
