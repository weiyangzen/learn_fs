# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/window.c

Vorbis window coefficient table and window application implementation. The bulk of the file is static precomputed window data for legal Vorbis block sizes.

Important contents:
- Includes `os.h`, `misc.h`, and `window.h`.
- Defines static half-window coefficient arrays:
  - `vwin64[32]`
  - `vwin128[64]`
  - `vwin256[128]`
  - `vwin512[256]`
  - `vwin1024[512]`
  - `vwin2048[1024]`
  - `vwin4096[2048]`
  - `vwin8192[4096]`
- Defines `vwin[8]`, an index table mapping window number to the corresponding coefficient array.
- `_vorbis_window_get(int n)` returns `vwin[n]`.
- `_vorbis_apply_window(float *d, int *winno, long *blocksizes, int lW, int W, int nW)` zeros samples outside overlap regions and applies the appropriate left and right overlap windows.

Control-flow summary:
- `_vorbis_apply_window()` normalizes previous/next window flags when the current block is short.
- It selects left and right window tables using `winno[lW]` and `winno[nW]`.
- It computes block sizes and overlap bounds:
  - left overlap begins at `n/4 - ln/4`
  - left overlap ends at `leftbegin + ln/2`
  - right overlap begins at `n/2 + n/4 - rn/4`
  - right overlap ends at `rightbegin + rn/2`
- It zeros leading samples, multiplies left overlap by ascending left window coefficients, multiplies right overlap by descending right window coefficients, and zeros trailing samples.

Integration points:
- Used by libvorbis synthesis/analysis block processing for MDCT lapping.
- Declared in `window.h`.
- Related to `vorbisfile.c` crosslap logic, which uses public/internal Vorbis window access for splicing decoded PCM.

Risk and review signals:
- `_vorbis_window_get()` does no bounds checking; callers must pass valid window indexes 0..7.
- `_vorbis_apply_window()` assumes `blocksizes`, `winno`, and `d` describe a legal Vorbis block/window configuration.
- Static table edits would directly affect codec reconstruction accuracy.
- The coefficient tables are data-heavy but behaviorally simple.

Filesystem relevance:
- No filesystem logic. This is codec DSP support data and windowing code.
