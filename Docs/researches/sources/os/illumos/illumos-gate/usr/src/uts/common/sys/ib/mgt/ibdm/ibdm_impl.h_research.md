# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibdm/ibdm_impl.h

## Scope

Private implementation header for IBDM. It defines Device Management request types, GID probe state, global module state, transaction-ID layout, DM MAD sizing, timeout defaults, message access macros, debug hooks, and helper types.

## APIs And Structures

- Request type flags identify ClassPortInfo, IOUnitInfo, IOCInfo, service entries, IOU diagnostic code, and IOC diagnostic code requests.
- `ibdm_taskq_args_t` carries IBMF handle, message, and opaque args into taskq processing.
- GID probe state flags model discovery progress from not-done through ClassPortInfo, IOUnitInfo, IOC details, completion, skipped, failed, and Cisco set-ClassPortInfo activation.
- Cisco FC gateway constants identify a special vendor/device combination and define OUI extraction from GUIDs.
- `ibdm_gid_t` is a linked-list node containing destination GID high/low halves.
- `ibdm_dp_gidinfo_t` is the per-Device-Protocol-GID probe object: mutex, state, reprobe flag, IOU pointer, pending command count, QP handle, transaction ID bounds, LIDs/GIDs/GUIDs/P_Key, redirect info, IBMF/SAA handles, timeouts, GID list, response timeout, IOC count, HCA list, previous IOU, Cisco probe CV/flags, and SL fields.
- `ibdm_t` is global IBDM state: global mutexes, HCA list, GID probe list, CVs, probe/busy counters, transaction ID counter, IBT client handle, registered ibnex callback, and previous-IOU flag.
- `ibdm_saa_event_arg_t` packages SAA event callback information for taskq use.

## Constants And Macros

- Transaction IDs are split into upper 32 bits per GID and lower 32 bits per MAD using `IBDM_GID_TRANSACTIONID_SHIFT` and mask.
- DM MAD size is 256 bytes, with a 40-byte Device Management MAD header after the common MAD/RMPP/access-key fields.
- Defaults include 4-second timeout and 3 retries.
- `IBDM_TIMEOUT_VALUE(t)` converts seconds to ticks.
- `IBDM_OUT_IBMFMSG_MADHDR`, `IBDM_IN_IBMFMSG_MADHDR`, status/attr/attrmod, and payload-cast macros simplify IBMF message parsing.
- `IBDM_GIDINFO2IOCINFO()` indexes IOU IOC arrays.
- `IBDM_IS_IOC_NUM_INVALID()` validates IOC slot numbers.
- `IBDM_INVALID_PKEY()` recognizes invalid full or limited P_Key values.

## Dependencies

- Includes `ibdm_ibnex.h` and IBTL implementation utility headers.
- Depends on IBMF message layout, SAA handles/events, IB DM attributes, and byte-order helpers such as `b2h16()` and `b2h32()`.

## Risks And Invariants

- `gl_mutex` protects GID probe state, timeout ID, pending commands, and nested IOC/service timeout IDs.
- Global `ibdm_mutex`, HCA-list mutex, and ibnex callback mutex protect distinct parts of module state; lock-order annotation requires global state before GID state.
- Transaction-ID uniqueness depends on bounded practical assumptions for GID count and per-GID MAD count.
- Redirect fields must be honored after ClassPortInfo redirect, or subsequent DM MADs may be sent to the wrong destination.
- Debug dump functions compile to no-ops outside DEBUG builds.
