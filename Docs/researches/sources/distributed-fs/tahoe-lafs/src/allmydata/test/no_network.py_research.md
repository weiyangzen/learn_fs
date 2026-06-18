# sources/distributed-fs/tahoe-lafs/src/allmydata/test/no_network.py

## Purpose
This file implements Tahoe-LAFS's single-process no-network grid test harness. It creates clients and storage servers in one `MultiService`, stores real shares on disk, and connects components with local wrappers that mimic Foolscap remote references without network tubs or introducers.

## Important APIs, Types, And Functions
Key types include `LocalWrapper`, `NoNetworkServer`, `NoNetworkStorageBroker`, `_NoNetworkClient`, `SimpleStats`, `NoNetworkGrid`, and `GridTestMixin`. Helper functions include `fireNow`, `wrap_storage_server`, and `create_no_network_client`. `GridTestMixin` exposes high-use test helpers such as `set_up_grid`, `restart_client`, `iterate_servers`, `find_uri_shares`, `copy_shares`, `restore_all_shares`, `delete_shares_numbered`, `corrupt_all_shares`, `GET`, and `PUT`.

## Control Flow
`NoNetworkGrid.__init__` creates storage servers, wraps them in `LocalWrapper`/`NoNetworkServer`, rebuilds the server list, and asynchronously creates clients. `_check_clients` rethrows setup failures caused by asynchronous work kicked off during construction. `LocalWrapper.callRemote` wraps arguments, optionally fails or hangs, invokes `remote_<method>`, wraps bucket reference returns, and records call counts. `GridTestMixin.set_up_grid` installs the grid under a service parent and records web ports/base URLs.

## State, Persistence, And Dependencies
Storage server state is persisted as share files in temporary server directories. Client configs are written under `basedir/clients/.../tahoe.cfg`. Server membership lives in `servers_by_number`, `wrappers_by_id`, and `proxies_by_id`, while each client's `_servers` field is refreshed after topology changes. HTTP helpers depend on `treq`; storage semantics depend on real `StorageServer` and `FoolscapStorageServer`.

## Risks And Test Signals
This harness is faster than full network system tests but omits introducers and real tubs. It is useful for checker, verifier, repairer, web, and share-manipulation tests. Risks include reference-cycle setup, incomplete broker methods returning empty placeholders, and local-wrapper behavior diverging from real Foolscap serialization or disconnect semantics.
