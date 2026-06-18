# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mdesc.h

Purpose: Defines the external machine-description format and API for logical domains receiving a virtual machine description from the hypervisor.

Key definitions:
- Header offsets and sizes: `MD_HEADER_*`, `MD_HEADER_SIZE`, `MD_ELEMENT_SIZE`.
- Transport version: `MD_TRANSPORT_VERSION`.
- Element tags: list end, null, node, node end, property arc/value/string/data.
- Opaque handles: `md_t`, `mde_cookie_t`, `mde_str_cookie_t`, `md_diff_cookie_t`.
- Invalid cookie/generation constants.

Key APIs:
- Lifecycle and metadata: `md_init_intern()`, `md_fini()`, `md_node_count()`, `md_root_node()`, `md_get_gen()`, `md_get_bin_size()`.
- Lookup/walk: `md_find_name()`, `md_scan_dag()`, `md_walk_dag()`.
- Property access: `md_get_prop_val()`, `md_get_prop_str()`, `md_get_prop_data()`, `md_get_prop_arcs()`.
- Diff interface: `md_diff_init()`, `md_diff_added()`, `md_diff_removed()`, `md_diff_matched()`, `md_diff_fini()`.
- `mdesc` device ioctls for quote buffer sizing/discard.

Important detail: The DAG walker passes both parent and current node to callbacks because nodes can have multiple parents, but the walk visits each node once.

Relevance to subset A: Virtualization/platform hardware description support.
