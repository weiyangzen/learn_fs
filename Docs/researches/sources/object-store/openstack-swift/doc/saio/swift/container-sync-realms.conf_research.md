# sources/object-store/openstack-swift/doc/saio/swift/container-sync-realms.conf

## Purpose
Defines the SAIO container-sync realm named `saio`.

## Important Sections
The `[saio]` section sets `key`, `key2`, and `cluster_saio_endpoint = http://127.0.0.1:8080/v1/`.

## Control Flow and Integration
Container sync middleware/daemon reads this file to authenticate and locate the target cluster endpoint for sync realm references. `key` and `key2` support shared-secret rotation.

## State, Risks, and Test Signals
The file does not persist object state but controls cross-cluster synchronization authorization. The `changeme` keys are test-only and unsafe in production. Test signal is container-sync acceptance of the realm and successful internal sync calls to the SAIO proxy.
