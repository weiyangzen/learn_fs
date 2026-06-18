# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/label.h

## Purpose
Trusted Extensions label API definitions for binary labels, ranges, multilevel ports, and kernel label reference objects.

## Main Interfaces
- Declares opaque `m_label_t` and compatibility aliases `blevel_t`, `bclear_t`, `bslabel_t`, and related label types from label macro internals.
- Defines dominance/equality check constants and label names `ADMIN_LOW` and `ADMIN_HIGH`.
- Defines `m_range_t`/`blrange_t` for lower and upper label ranges.
- Defines multilevel port structures `tsol_mlp_t`, `tsol_mlp_entry_t`, and `tsol_mlp_list_t`.
- Defines `ts_label_t`, which combines a reference count, DOI, flags, and binary sensitivity label.
- Defines `DEFAULT_DOI` and label flags `TSLF_UNLABELED`, `TSLF_IMPLICIT_IN`, and `TSLF_IMPLICIT_OUT`.
- Provides macros `CR_SL` and `is_system_labeled`.
- Declares label comparison/manipulation functions such as `blequal`, `bldominates`, `blstrictdom`, `blinrange`, `blmaximum`, `blminimum`, `bsllow`, `bslhigh`, `bclearlow`, and `bclearhigh`.
- Declares kernel label allocation/reference routines: `label_init`, `labelalloc`, `labeldup`, `label_hold`, `label_rele`, `label2bslabel`, `label2doi`, and `label_equal`.

## Dependencies And Relationships
Includes `sys/types.h`, `sys/cred.h`, `sys/vnode.h`, and `sys/tsol/label_macro.h`. Used by Trusted Extensions credential, vnode, networking, and policy enforcement code.

## Research Notes
The public-looking names wrap a compact binary label implementation in `label_macro.h`; reference-counted `ts_label_t` is the kernel object used to carry labels through credentials and network attributes.
