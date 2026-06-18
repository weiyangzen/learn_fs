# sources/object-store/garage/src/model/k2v/mod.rs

## Purpose
This file declares the K2V model submodules.

## Important APIs, types, and functions
It exports `causality`, `seen`, `item_table`, `rpc`, and `sub`. These modules implement vector-clock tokens, range seen markers, the K2V item table, RPC insert/poll logic, and subscription management.

## Control flow
There is no runtime logic in this file.

## State and persistence behavior
No state is stored here. K2V state is in `item_table`, local timestamp DB trees in `rpc`, and transient subscriptions in `sub`.

## Dependencies and integration points
The module is feature-gated from `model/lib.rs` and `garage.rs` by the `k2v` feature.

## Risks and edge cases
Changing module visibility or names affects the K2V API, Garage initialization, and tests.

## Test signals
Compilation with and without the `k2v` feature is the primary signal for this file.
