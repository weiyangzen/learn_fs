# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/psymodel.c

This file implements LAME's Layer III psychoacoustic model for the 9front-imported `mp3enc` tree. It computes masking thresholds, perceptual entropy, block switching decisions, and mid/side stereo guidance from PCM windows and FFT energy.

Key responsibilities:
- Lazily initializes psychoacoustic state and FFT tables through `psymodel_init()` and `init_fft()`.
- Provides two analysis paths:
  - `L3psycho_anal()`: older ISO/GPSYCHO-style analysis using unpredictability and tonality from long/short FFTs.
  - `L3psycho_anal_ns()`: nspsytune-style analysis using spectral peak tonality, high-pass attack detection, additive masking, and extra mid/side fixes.
- Computes long- and short-block energy/masking data into `III_psy_ratio` structures.
- Maintains a one-granule delay: current analysis is saved in `gfc`, while previous-granule ratios, perceptual entropy, and block types are returned to the encoder.
- Determines block types (`NORM_TYPE`, `START_TYPE`, `SHORT_TYPE`, `STOP_TYPE`) from attack/PE history.
- Computes mid/side masking thresholds and `ms_ratio`/`ms_ratio_next` signals for joint stereo decisions.
- Builds Bark-scale partition bands, scalefactor-band mappings, spreading functions, ATH partition values, demasking thresholds, and temporal masking decay in `L3para_read()`.
- Initializes persistent history buffers, old block types, unpredictability limits, spreading-function index ranges, and nspsytune state in `psymodel_init()`.

Important functions:
- `L3psycho_anal(...)`: full classic psychoacoustic analyzer.
- `mask_add(...)`: nspsytune additive simultaneous masking combiner.
- `L3psycho_anal_ns(...)`: nspsytune psychoacoustic analyzer with attack/pre-echo controls.
- `s3_func(FLOAT8 bark)`: Bark-domain spreading function.
- `L3para_read(...)`: derives psychoacoustic partition/scalefactor mapping and spreading tables from samplerate.
- `psymodel_init(lame_global_flags *gfp)`: initializes all persistent psychoacoustic model state.

Control/data flow:
- The encoder calls this file from `encoder.c` before MDCT/quantization.
- Input PCM buffers are transformed through `fft_long()` and `fft_short()` for left/right channels; joint stereo creates mid/side FFT spectra from those results.
- Per-line FFT energies are grouped into critical-band partitions.
- Thresholds are convolved with `s3_l`/`s3_s` spreading functions.
- Partition data is remapped to MPEG scalefactor bands using `bu_*`, `bo_*`, `w1_*`, and `w2_*` tables.
- Results populate `gfc->en[]`, `gfc->thm[]`, `gfc->pe[]`, `gfc->tot_ener[]`, `gfc->blocktype_old[]`, and optional `pinfo` analysis fields.
- Returned `masking_ratio` and `masking_MS_ratio` feed quantization threshold calculation in `quantize_pvt.c`.

Notable behavior:
- Classic mode estimates unpredictability for low spectral lines from long FFT history and for higher lines from short FFTs.
- nspsytune mode applies an fs/4 high-pass FIR for attack detection over 12 sub-short blocks.
- nspsytune applies short-block pre-echo attenuation based on current and previous attack positions.
- `no_short_blocks` forces long-block decisions.
- Joint stereo generally forces both channels to share block type unless `allow_diff_short` is enabled and MS stereo is not used.
- `safejoint` reduces the nspsytune MS masking relaxation from `NS_MSFIX` to a stricter value.
- `analysis` mode fills plotting/diagnostic arrays.

Dependencies:
- Includes `util.h`, `encoder.h`, `psymodel.h`, `l3side.h`, `tables.h`, and `fft.h`.
- Relies on internal fields in `lame_internal_flags`, especially psychoacoustic history arrays defined in `util.h`.
- Uses ATH and scalefactor-band data initialized elsewhere in the encoder setup.

Risks and edge cases:
- This file is heavily stateful; first-call initialization and one-granule delayed returns must stay synchronized with encoder buffering.
- `energy` is treated as a 4-channel array in the implementation, while `psymodel.h` declares the parameter as `FLOAT8 ener[2]`; C array decay hides this ABI-wise but the declaration is misleading.
- Several static/local arrays assume maximum channel count including derived M/S channels.
- Assertions guard partition counts and block-type invariants but may disappear in non-debug builds.
- The nspsytune path uses hard-coded regression coefficients and attack thresholds; behavior is sensitive to samplerate and encoder quality settings.
