# sources/test-tools/fio/dataplacement.c

Purpose: Implements fio data placement support for Flexible Data Placement (FDP) and streams, mapping write IOs to placement identifiers through random, round-robin, or scheme-file policies.

Important APIs/functions: Public functions are `dp_init()`, `fdp_free_ruhs_info()`, and `dp_fill_dspec_data()`. Internal helpers `fdp_ruh_info()`, `init_ruh_info()`, and `init_ruh_scheme()` fetch or construct reclaim unit handle information and optional offset-to-PLI schemes.

Control flow: `dp_init()` walks each file in a thread. For streams mode, `init_ruh_info()` builds `fio_ruhs_info` directly from user-supplied stream IDs. For FDP, it asks the IO engine's `fdp_fetch_ruhs` callback for the RUH count, reallocates to include PLIs, fetches the full list, validates optional user-selected indices, and stores a reduced PLI list on the file. If scheme selection is enabled, `init_ruh_scheme()` reads CSV lines of `start,end,pli` into a fixed-size scheme array. During each IO, `dp_fill_dspec_data()` clears non-write or uninitialized IOs; otherwise it selects a PLI by round-robin, scheme match, or random selection and writes `io_u->dtype`/`dspec`.

State/persistence: Placement metadata is per `fio_file` in `ruhs_info` and `ruhs_scheme`. Round-robin position is mutable in `pli_loc`; random selection uses `td->fdp_state`.

Dependencies/integration: Requires fio thread/file/io_u structures, engine support for `fdp_fetch_ruhs`, shared allocation helpers, and logging/debug channels. The selected fields are consumed by engines that translate `dtype/dspec` into device directives.

Risks: Scheme parsing is permissive and lacks range-order validation. `fdp_free_ruhs_info()` returns early when `ruhs_info` is null, leaving `ruhs_scheme` allocated if that impossible-looking split state occurs. FDP index validation treats user IDs as indices into fetched PLIs, not raw PLIs, which must match documentation.

Test signals: Tests should cover streams without IDs rejection, FDP engines without fetch callback, selected index bounds, max PLI clamping, scheme default-to-zero, and write-only directive population.
