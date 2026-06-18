# sources/object-store/daos/src/vos/vos_overhead.c

## Purpose
`vos_overhead.c` exposes metadata sizing helpers for VOS pools, containers, SCM cutoff, and tree overhead estimation. It is a bridge from durable layout/tree classes to metadata sizing tools.

## Important APIs, Types, And Functions
The file exports `vos_pool_get_msize`, `vos_container_get_msize`, `vos_pool_get_scm_cutoff`, and `vos_tree_get_overhead`. `vos_tree_get_overhead` maps `enum VOS_TREE_CLASS` values to dbtree or evtree classes/orders: container, object, dkey, akey, single value, array, and VEA.

## Control Flow
The overhead call zeroes the output structure, dispatches arrays to `evt_overhead_get`, maps other tree classes to btree class/order pairs, and calls `dbtree_overhead_get`. Unsupported classes assert.

## State And Persistence
There is no mutable state. The return values are derived from durable format structure sizes and tree configuration constants, so changes in layout structs or tree orders flow into overhead estimates.

## Dependencies And Integration Points
It depends on VOS layout/internal constants, dbtree overhead APIs, evtree overhead APIs, and VEA tree order definitions. `vos_size.c` consumes these helpers to generate YAML used by metadata overhead estimation.

## Risks
The main risk is stale mappings when new tree classes, layout versions, or btree orders are introduced. A wrong order/class pairing causes capacity estimates to drift from runtime allocation behavior.

## Test Signals
Run the VOS size generator and compare expected tree classes, non-zero node/record sizes, and SCM cutoff. Tests should fail if a new `VOS_TREE_CLASS` is not mapped.
