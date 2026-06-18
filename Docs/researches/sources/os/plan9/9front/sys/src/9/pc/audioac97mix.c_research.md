# File Research: sources/os/plan9/9front/sys/src/9/pc/audioac97mix.c

AC'97 codec mixer layer shared by the AC'97 controller driver.

Key responsibilities:
- Defines AC'97 codec register constants, capability bits, and volume controls.
- Implements volume get/set callbacks for master, headphone, audio, CD, line, mic, record gain, sample rate, and delay.
- Publishes mixer reads/writes through generic audio volume helpers.
- Resets codec power state and enables variable-rate audio when supported.

Important behavior:
- Capability masks hide controls unsupported by the codec.
- `speed` writes front DAC and ADC rate registers and then records the actual accepted rate.
- `delay` is a software playback latency setting stored in `Audio`.
- Reports AC'97 extension support such as VRA, SPDIF, and extra DACs.

Dependencies:
- Depends on controller-supplied codec register callbacks and the generic `audioif.h` volume parser/formatter.

Notable risks:
- If VRA is absent, the driver prints a warning but still exposes the speed control.
- The mixer allocation failure leaves the controller without volume callbacks.
