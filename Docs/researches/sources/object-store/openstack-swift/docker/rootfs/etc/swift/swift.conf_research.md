# sources/object-store/openstack-swift/docker/rootfs/etc/swift/swift.conf

## Purpose
Docker rootfs global Swift config with concrete hash path secrets and a default single-replica storage policy.

## Important Sections
`[swift-hash]` sets fixed prefix/suffix values. `[storage-policy:0]` defines `1replica` as the default replication policy. An EC42 policy is present but commented out.

## Control Flow and Integration
All Swift services in the container read this file for path hashing and policy registry setup. The single-replica policy simplifies Docker development.

## State and Persistence Behavior
Hash secrets must remain stable for existing data. The one-replica default affects durability and ring placement expectations. Enabling the commented EC policy would require matching rings and object-server/reconstructor support.

## Risks and Test Signals
Single replica is not durable and is intended for local/container testing. Test signal is service startup with policy registry and successful object placement under policy 0.
