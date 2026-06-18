# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mixer.h

Purpose: Defines audio mixer modes, default audio format settings, mixer ioctls, and variable-sized mixer control/sample-rate structures.

Key definitions:
- Modes: `AM_MIXER_MODE`, `AM_COMPAT_MODE`.
- Defaults: 8000 Hz, mono, 8-bit u-law, mid gain.
- Mixer ioctls for multiple/single open, sample rates, info, channel info, and mode get/set.
- `am_control_t`: audio device info plus variable channel-open bitmap.
- `am_sample_rates_t`: play/record type, flags, count, and variable sample-rate array.

Important detail: Macros compute variable structure sizes based on channel/sample-rate count.

Relevance to subset A: Legacy audio ABI, not filesystem-specific.
