# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/dca.h

## Role

Private header for the Deimos cryptographic accelerator driver based on Broadcom 582x hardware.

## Scope

The file explicitly states everything is private to the DCA device driver.

## Driver Identity and Tunables

- Driver name: `dca`
- Manufacturer id: `SUNWdca`
- Work/request watermarks for MCR1 and MCR2.
- Limits:
  - two MCRs.
  - max requests per MCR.
  - max fragments.
  - preallocated work structures.
  - max packet size differs on x86 due to rootnex behavior.

## Algorithm Constants

Includes sizes and ranges for DES, 3DES, DSA, SHA1, MD5-HMAC, SHA1-HMAC, RSA, IVs, and key sizes.

## Mechanism/Operation Types

- RSA modes: encrypt, decrypt, sign, verify, sign recover, verify recover.
- DSA modes: sign, verify.
- DCA mechanism enum for DES CBC, 3DES CBC, DSA, RSA X.509, RSA PKCS.
- Defines `SUN_CKM_DSA`.

## FMA

- `dca_fma_eclass_t`: hardware device, timeout, none.

## Core Structures

- `dca_device`: PCI vendor/device/model identity.
- `dca_chain`: DMA data buffer chain entry with descriptor/buffer kernel addresses, DMA handles, and physical addresses.
- `dca_listnode`: double linkage plus second linkage pair.
- `dca_rng` and `union dca_parameters`.
- `dca_ctx_t`: crypto context with mechanism, mode, atomic flag, RSA/DSA modulus data, DES/3DES IV/key/residual data, and duplicate input data.
- `dca_request_t`: full request/job descriptor, including KCF request handle, input/output data, context, DMA context/input/output buffers, programmed MCR fields, callback, flags, algorithm parameters, stats, pre-mapped chains, dynamic user-buffer chains, context-page offset, and destroy flag.
- `dca_work_t`: MCR work item with DMA mapping and request slots.
- `dca_worklist_t`: per-MCR queue state, locks, condition variable, freelists, wait/run queues, scheduling timeout, flow-control settings, drain flag, and kstats.
- `dca_stat_t`: kstat layout.
- `dca_cookie_t`: ioctl blocking state.
- `dca_t`: per-device instance with devinfo, registers, interrupt locks, worklists, model/id, kstats, RNG buffers/state, FMA capabilities, and context list.

## Request and Device Flags

Request flags include in-place, scatter, gather, no-cache, encrypt/decrypt, triple-DES, and atomic.

Device flags include failed, power management, and RNG-SHA1 support.

## Hardware Register Definitions

Defines PCI config offsets/bit fields, command/status registers, DMA control/status bits, MCR offsets/sizes/flags, data-buffer descriptor offsets, and hardware context offsets for 3DES, IPsec, RSA, and DSA operations.

## Access Macros

- `PUTMCR*`, `GETMCR*`
- `PUTDESC*`
- `PUTCTX*`
- `CTXBCOPY`
- `GETCSR`, `PUTCSR`, `SETBIT`, `CLRBIT`
- alignment and word extraction helpers.
- hardening check `CHECK_REGS()`.
- queue and worklist helpers.

## Debug and PKCS#11 Constants

Under `DEBUG`, defines debug categories and `DBG`.

The file locally defines PKCS#11 object/key attribute constants needed by the driver.

## Function Surface

Declares driver routines for:

- Debug/error reporting.
- 3DES context/init/update/final/atomic/free.
- RSA init/start/atomic/free.
- DSA sign/verify/init/atomic/free.
- RNG and random buffer management.
- Kstat initialization.
- Request allocation/free/destruction, queue manipulation, DMA chain binding/unbinding, starting jobs, completion, data length/gather/scatter/residual handling, duplicate crypto data, I/O validation, scatter/gather checks, key attribute lookup, buffer address extraction, coalescing, bignum helpers, DMA handle checking, and context freeing.

## Research Relevance

Important for hardware crypto provider internals and KCF provider implementation. It shows DMA, scatter/gather, request scheduling, device hardening, FMA, and asymmetric/symmetric operation integration.
