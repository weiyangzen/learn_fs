# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dld_impl.h

## Scope

Complete file read, 352 lines. This is the kernel-private implementation header for DLD stream state and helper macros.

## Public Surface

It defines control minor names/numbers, DLD stream type flags, stream modes (`DLD_UNITDATA`, `DLD_FASTPATH`, `DLD_RAW`), and passive-state enum values.

The central type is `struct dld_str_s`, with fields for major/minor, PPA, STREAMS queues, stream type, DLPI state/style/SAP, MAC handles, promiscuity handles, MAC info, priority, notification state, mode, native/poll/direct/LSO state, passive state, flow-control dummy message, pending DLPI queue state, DLS linkage, multicast state, rx callback, active counts, task queue list, private driver data, lowlink and non-IP flags.

It provides data-thread count macros `DLD_DATATHR_INC` and `DLD_DATATHR_DCR`, DLD string/protocol/flow/drv function prototypes, option flags, autopush state type `dld_ap_t`, queue-full macros `DLD_SETQFULL` and `DLD_CLRQFULL`, `DLD_TX`, and debug macro `DLD_DBG`.

## Behavior And Integration

DLD implementation files use this header to manage each open DLPI stream and its interaction with MAC clients, DLS link state, direct transmit, polling, and flow control.

## Dependencies And Invariants

The header documents protection for each field: write-once, serializer-protected, mutex/rwlock-protected, or reference protected. Correct behavior depends on honoring those locking annotations.

## Risks

`DLD_SETQFULL` and `DLD_CLRQFULL` manipulate STREAMS queue state and `ds_tx_flow_mp` under `ds_lock`; misuse can lose flow-control messages. `DLD_DATATHR_DCR` assumes the count is positive and broadcasts only on zero. This is private kernel state and should not be used by external modules.
