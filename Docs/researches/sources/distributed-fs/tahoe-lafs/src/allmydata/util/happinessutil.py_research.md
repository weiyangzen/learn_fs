# sources/distributed-fs/tahoe-lafs/src/allmydata/util/happinessutil.py

## Purpose

This module computes and explains Tahoe's "servers of happiness" placement metric: how many distinct servers can be matched to distinct shares such that any needed subset can recover the file. It supports upload/repair placement diagnostics.

## APIs and control flow

`failure_message()` chooses a user-facing explanation based on peer count, needed shares `k`, requested happiness, and effective happiness. `shares_by_server()` inverts a share-to-peers map. `merge_servers()` deep-copies a sharemap and folds in upload tracker buckets. `servers_of_happiness()` converts the sharemap into a bipartite flow network, then runs Edmonds-Karp using `residual_network()` and `augmenting_path_for()` from immutable upload code to compute maximum matching size. `_flow_network_for()` and `_reindex()` build dense integer-indexed graph vertices.

## State, dependencies, risks, and tests

State is in-memory share/server maps. Dependencies are `deepcopy` and `allmydata.immutable.happiness_upload` flow helpers. Integration is direct with erasure-coded upload placement, repair assessment, and user diagnostics when placement cannot satisfy policy.

Risks include divergence from the similar happiness_upload implementation, graph indexing differences, empty maps, duplicate/missing share numbers, and expensive flow computation for large maps. Test signals should cover empty, perfectly distributed, clustered, and tracker-merged sharemaps; failure-message branch selection; non-contiguous share IDs; and parity with upload placement calculations.
