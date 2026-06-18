# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_happiness.py

Purpose: tests Tahoe's share placement and "servers of happiness" algorithms. It covers maximum-flow helpers in immutable upload placement, placement under readonly/existing-share constraints, property-based placement invariants, and utility functions that merge and invert share/server mappings.

Important APIs and types include `HappinessUploadUtils`, `Happiness`, `PlacementTests`, `FakeServerTracker`, and `HappinessUtilTests`. The implementation under test includes `happiness_upload._servermap_flow_graph`, `residual_network`, `_compute_maximum_graph`, `share_placement`, `calculate_happiness`, plus `servers_of_happiness`, `shares_by_server`, and `merge_servers`.

Control flow tests trivial flow graph cases, then builds concrete peer/share sets with readonly peers and existing placements to assert generated share-to-peer mappings and calculated happiness. Several tests encode prior Hypothesis-discovered edge cases such as peers named with overlapping text, one peer with multiple shares, more shares than peers, no peers, and redistribution from a crowded server to an unused server. Property-based tests generate peer and share sets and assert every share is placed on an existing peer and happiness equals the minimum of peer count and share count when no readonly/existing constraints apply.

State and persistence are pure in-memory mappings: sets of peer IDs, share IDs, readonly peer IDs, `peers_to_shares`, and fake tracker objects with `get_serverid` and `buckets`. There is no filesystem or storage-server persistence.

Dependencies include Twisted Trial, Hypothesis `text`/`sets`, the immutable upload placement module, happiness utility functions, and `ShouldFailMixin` for asserting invalid input to `shares_by_server`.

Risks covered include undercounting or overcounting maximum matchings, failing to place all shares, using peers outside the candidate set, mishandling readonly peers that already hold shares, not redistributing when it would improve happiness, duplicate servers reducing effective diversity, and invalid mapping shapes. Residual risk is that deterministic placement details are asserted only for selected cases; many valid maximum matchings may differ, so tests focus on happiness invariants where possible.

Test signals include exact residual network/capacity matrices for a one-edge graph, exact placement maps for simple and readonly cases, happiness counts for 0, 2, 3, 4, 5, 7, and 100 cases, Hypothesis property assertions, `merge_servers` expected dictionaries, `shares_by_server` inverse mappings, and an expected `AssertionError` for non-set server mappings.
