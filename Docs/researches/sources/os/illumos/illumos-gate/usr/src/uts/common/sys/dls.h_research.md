# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dls.h

## Scope

Complete file read, 160 lines. This header defines the public kernel-facing Data-Link Services interface and PPA/minor conversion helpers.

## Public Surface

It defines `DLS_MODULE_NAME`, `DLS_INFO`, PPA conversion macros `DLS_PPA2INST`, `DLS_PPA2VID`, `DLS_PPA2MINOR`, `DLS_VIDINST2PPA`, and `DLS_MINOR2INST`.

Under `_KERNEL`, it defines `DLS_MAX_PPA`, `DLS_MAX_MINOR`, receive callback type `dls_rx_t`, forward handle types, SAP/promiscuity constants, and prototypes for DLS open/close/bind/unbind, promiscuous and multicast control, header construction, RX callback management, device-network open/close/rebuild/rename/create/destroy/recreate/hold/release/property wait/query functions, link visibility, management door setup, management create/destroy/update/get functions, iteration, and MAC-name-to-link-id lookup.

## Behavior And Integration

DLD uses DLS to bind streams to MAC-backed data links, manage VLAN PPA mapping, multicast/promiscuous state, and integrate with data-link management state.

## Dependencies And Invariants

The PPA mapping uses `ppa = vid * 1000 + inst`; valid instances are 0-999. Minor numbers are instance plus one.

## Risks

PPA arithmetic encodes VLAN and instance in a decimal-style range, so values outside `DLS_MAX_PPA` can alias or exceed expected minor ranges. Most prototypes are kernel-only and depend on MAC/DLS lifetime rules outside this header.
