# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/mem_config_stubs.c

## Purpose

Provides stub definitions for memory cage and memory configuration interfaces on builds/platforms where the real implementation is absent or disabled.

The file comments note these should be in a platform stubs file.

## Main Responsibilities

- Define cage globals so references link without full cage support.
- Provide no-op or success-returning implementations for cage and kphysm setup APIs.
- Keep callers able to compile while making cage behavior effectively disabled.

## Data Provided

- `int kcage_on`
- `kthread_id_t kcage_cageout_thread`
- `pgcnt_t kcage_freemem`
- `pgcnt_t kcage_throttlefree`
- `pgcnt_t kcage_minfree`
- `pgcnt_t kcage_desfree`
- `pgcnt_t kcage_needfree`
- `pgcnt_t kcage_lotsfree = 1`

## Stubbed Functions

- `kphysm_setup_func_register(...)`
  Returns success on non-x86 or xPV builds covered by the preprocessor guard.

- `kphysm_setup_func_unregister(...)`
  No-op under the same guard.

- `kcage_create_throttle(pgcnt_t npages, int flags)`
  Returns `0`, meaning no cage throttling behavior is applied.

- `kcage_cageout_init(void)`
  No-op.

- `kcage_cageout_wakeup()`
  No-op.

- `kcage_tick()`
  No-op.

- `kcage_current_pfn(pfn_t *pfn)`
  Returns `0` without setting an active cage PFN.

## Locking and Side Effects

There is no locking and no meaningful state transition. These functions are compatibility shims only.

## External Dependencies

Includes page, memory configuration, and memory cage headers to match real interface types.

## Research Notes

Any code running with these stubs must not rely on actual cage reclaim, throttling, or kphysm callback behavior. The stubs are deliberately permissive and should be treated as platform/build compatibility, not functional memory DR support.
