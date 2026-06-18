# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge.h

## Purpose

`nxge/nxge.h` is the primary private/public driver header for the Neptune/NIU `nxge` Ethernet driver. It defines diagnostic ioctl numbers, driver parameters, statistics, interrupt state, ring/group virtualization state, the main per-instance `nxge_t` state object, kstat layouts, and core prototypes.

## Main Interfaces

The `NXGE_IOC` command namespace defines diagnostic and maintenance ioctls for register reads/writes, ring descriptor inspection, resets, MII access, tracing, register dumps, TCAM access, error injection, RX classification, and RX hashing.

Driver constants define module info, STREAMS packet sizes/watermarks, timers, compatibility strings, and status values.

`nxge_param_index_t` enumerates all tunable or reportable driver parameters, including instance metadata, firmware/port mode, autonegotiation, advertised capabilities, pause settings, DMA channel counts and groups, RDC defaults, interrupt moderation, classification, TCAM/hash controls, debug flags, and dump controls.

`nxge_param_t` describes named dispatch parameters with get/set callbacks, type flags, min/max/current/old values, firmware-code name, and user-visible name. Parameter flags encode read/write/shared/private, subsystem category, initialization-only, property source, numeric base, visibility, and array metadata.

The file defines link-loopback modes, MAC state, DLPI address structures, multicast hash tables, filters, port statistics, aggregate statistics/kstat handles, interrupt state, logical-device/group vectors, Crossbow/hybrid-I/O group and ring handles, share handles, and the large `struct _nxge_t` per-device instance state.

`struct _nxge_t` aggregates devinfo, register handles, NPI handles, transceiver/MAC/IPP/TXC/classifier state, MAC framework handle, statistics, tunables, hardware-list pointer, platform/NIU type, DMA pools/rings/mailboxes, PHY/MII state, filters, timers, FMA state, port ring sizing, multi-MAC info, sun4v hypervisor state, link polling, magic value, LSO flag, LDOM/Hybrid I/O state, ring/group/share arrays, and NIU hardware type.

Kstat structures define named counters for port, RDC, RDC system, TDC, TXC, IPP, ZCP, MAC/XMAC/BMAC, FFLP, and multi-MAC state.

Core prototypes include `nxge_init()`, `nxge_uninit()`, diagnostic 64-bit get/put, PIO loop, and timer start/stop.

## Runtime Use

Driver attach allocates and initializes `nxge_t`, maps registers, configures DMA rings and classifier state, registers interrupts, exposes MAC rings/groups, creates kstats, and uses the parameter model for ndd/configuration interfaces. Runtime paths update statistics and use the ring/group/share structures for normal and hybrid I/O operation.

## Dependencies

Includes `nxge_mac.h`, `nxge_ipp.h`, and `nxge_fflp.h`, which provide many referenced types and constants. It also relies on MAC framework, DDI, kstat, DMA, MII, and platform-specific types from surrounding includes.

## Risks and Invariants

The loopback enum explicitly warns not to reorder values because driver code depends on order.

`nxge_t` is a large shared state structure with many locks and subsystem-owned fields. Changes require understanding attach/detach, interrupt, DMA, MAC, FMA, and hybrid-I/O interactions.

Array dimensions such as `NXGE_MAX_TDCS`, `NXGE_MAX_RDCS`, `NXGE_MAX_RDC_GROUPS`, and `NXGE_MAX_VRS` must remain consistent with hardware and included headers.

Diagnostic ioctls expose powerful low-level operations such as register writes, resets, TCAM writes, and error injection; callers must be privileged and state-aware.
