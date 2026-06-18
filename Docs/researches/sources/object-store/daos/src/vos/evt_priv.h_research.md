# sources/object-store/daos/src/vos/evt_priv.h

## Purpose
`evt_priv.h` defines the private evtree implementation contract shared by VOS event-tree source files. It contains durable-format constants, iterator/context structures, transaction helpers, rectangle filtering helpers, node/descriptor accessors, checksum helper declarations, search opcodes, context handle operations, and internal tree traversal/manipulation declarations.

## Important APIs, types, and functions
Key constants include `EVT_TX_MINOR_MAX_DF`, rebuild minor epoch ranges, node flags `EVT_NODE_LEAF`/`EVT_NODE_ROOT`, iterator states, `MAX_RECT_WIDTH`, `EVT_TRACE_MAX`, null offsets, node magic, and handle magic values. Core types are `struct evt_iterator`, `struct evt_trace`, `struct evt_context`, `struct evt_extent`, and `enum evt_find_opc`.

Important inline helpers include `evt_off2node`, `evt_off2desc`, `evt_tx_begin`, `evt_tx_end`, `evt_tcx_addref`, `evt_tcx_decref`, `evt_filter_rect`, `evt_epoch_uncertain`, `evt_ent2rect`, `evt_nd_off_rect_read_at`, `evt_node_is_leaf`, `evt_node_is_root`, `evt_node_entry_at`, `evt_node_desc_at`, and `evt_entry_punched`. Declared implementation hooks include descriptor checksum helpers, `evt_tcx_clone`, `evt_node_delete`, `evt_ent_array_sort`, `evt_ent_array_fill`, `evt_rect_cmp`, `evt_tcx2hdl`, `evt_hdl2tcx`, `evt_move_trace`, `evt_node_rect_read_at`, `evt_entry_fill`, and `evt_dtx_check_availability`.

## Control flow
The header has no standalone execution, but it shapes evtree control flow. Open contexts cache durable root metadata, tree order/depth, feature bits, umem instance, policy ops, descriptor callbacks, embedded iterator storage, and scratch trace space. Iterators use filters with extent and epoch ranges, options, direction, index, and sorted entry arrays. Traversal code uses trace entries from root to leaf, converts umem offsets to durable nodes/descriptors, filters rectangles differently for internal nodes versus leaf records, and delegates transaction boundaries to inline helpers.

## State and persistence behavior
`struct evt_context` bridges volatile handle state and persistent evtree state: it points at the durable root and umem pool while caching order/depth/features to reduce persistent reads. Node and descriptor helpers assert durable magic values. `evt_tx_begin`/`evt_tx_end` only create PMDK/umem transactions when the tree's umem instance supports transactions, preserving compatibility with DRAM and persistent backends. Minor epoch constants reserve upper bits for normal, rebuild, distributed transaction, and future record classes, which affects durable ordering and rebuild visibility.

## Dependencies and integration points
The header depends on public evtree declarations and VOS internals. It is consumed by evtree implementation files such as iterator, insert, delete, find, and tests. It integrates with VOS punch semantics, DTX availability checks, checksum layout, BIO address state, umem transactions, policy callbacks, and DAOS epoch/extent types.

## Risks and test signals
Risks include durable-format compatibility mistakes in minor epoch ranges, `MAX_RECT_WIDTH` violations, incorrect context refcount cleanup for embedded iterator arrays, filtering internal nodes too aggressively, transaction abort/commit misuse, and offset-to-pointer assertions masking corrupt persistent state. Tests should validate handle lifetime, PMEM and non-PMEM transaction paths, punch filtering, rebuild minor epoch ordering, checksum count/buffer calculations, node accessor invariants, and interoperability with `evt_iter.c` anchor/fetch/delete behavior.
