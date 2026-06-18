# sources/object-store/openstack-swift/doc/saio/swift/swift.conf

## Purpose
SAIO global Swift config defining hash path secrets and storage policies.

## Important Sections
`[swift-hash]` sets placeholder `swift_hash_path_prefix` and `swift_hash_path_suffix`. Storage policy 0 is replication policy `gold` and default. Policy 1 is replication policy `silver`. Policy 2 is erasure-coding policy `ec42` using `liberasurecode_rs_vand` with 4 data and 2 parity fragments.

## Control Flow and Integration
Swift rings and path hashing depend on the immutable hash prefix/suffix. Account, container, object, proxy, and background daemons read policies through Swift's storage policy registry.

## State and Persistence Behavior
Changing hash secrets after data exists makes stored paths unreachable. Policies determine object placement and on-disk policy datadirs; changing or removing policies affects object-server/reconstructor behavior.

## Risks and Test Signals
The `changeme` secrets are SAIO placeholders. Test signal is ring/policy loading and ability to PUT/GET objects under replicated and EC policies in the local environment.
