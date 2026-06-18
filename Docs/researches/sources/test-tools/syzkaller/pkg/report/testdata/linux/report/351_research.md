<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/351 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/351

## Purpose
This fixture validates lockdep informational parsing for a non-static key registration in VKMS/DRM cleanup, while another CPU panics on a lockdep warning. The expected title is `INFO: trying to register non-static key in vkms_atomic_crtc_destroy_state`.

## Important APIs, Types, And Functions
The primary marker is `INFO: trying to register non-static key.` followed by `register_lock_class` and lock acquisition frames. The meaningful subsystem path is `__flush_work`, `flush_work`, `vkms_atomic_crtc_destroy_state`, `drm_atomic_state_default_clear`, `drm_mode_setcrtc`, `drm_ioctl`, and `ksys_ioctl`. Interleaved panic-on-warn frames mention `lock_downgrade`.

## Control Flow
The reporter must treat the INFO lockdep report as primary, derive the title from the VKMS cleanup frame, and still set `PANICKED: Y` because another task triggers panic-on-warn during the same log window.

## State And Persistence
The header persists title and panicked state. The raw log includes a syzkaller reproducer fragment, DRM ioctl state, and a secondary lockdep warning/panic.

## Dependencies And Integration Points
It depends on lockdep info parsing, frame selection outside the immediate `register_lock_class` helper, interleaved task handling, and panic detection.

## Risks
The secondary `lock_downgrade` warning can steal the title if first-report/priority logic changes. The reproducer program text must be ignored as console context, not report content for title derivation.

## Test Signals
Expected output keeps the non-static-key title in `vkms_atomic_crtc_destroy_state` and marks panicked.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/351 -->
