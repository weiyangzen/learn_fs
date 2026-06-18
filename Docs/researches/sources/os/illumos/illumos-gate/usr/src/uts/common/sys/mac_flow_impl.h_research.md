# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_flow_impl.h

## Role

Private MAC flow implementation header for flow reference handling, quiescence, bandwidth control, flow entries, packet parse state, flow-table operations, and statistics helpers.

## Structure

Defines flow refhold/release/user-ref macros, flow mark/unmark macros, bandwidth/priority helpers, flow table size, flow lookup flags, callback/match signatures, flow states, entry flags/types, bandwidth control state and `mac_bw_ctl_t`, `flow_entry_t`, layer parse info, `flow_state_t`, `flow_ops_t`, `flow_tab_t`, flow table info, stats update macros, and flow lifecycle/table/bandwidth helper prototypes.

## Dependencies And Consumers

Includes param, atomic, time, synchronization, public flow, STREAMS, SDT, and net interface headers. Consumed by MAC flow/classifier, soft-ring, client, bandwidth, and datalink internals.

## Important Details

`FLOW_TRY_REFHOLD()` rejects incipient, quiesced, condemned, and no-datapath flows before data-path use. `FLOW_REFRELE()` may call `mac_flow_destroy()` while holding/releasing through the macro path, so callers must understand ownership. Bandwidth control is shared across related SRS queues and combines drop-threshold policing with bytes-per-tick shaping.

## Research Notes

Read completely: 597 lines, 17487 bytes.
