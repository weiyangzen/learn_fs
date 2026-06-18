# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/block.c

## Role

This is the libvorbis block, DSP, PCM buffering, windowing, overlap/add, and analysis/synthesis state management implementation. It is one of the core runtime files for Vorbis encode and decode.

## Block Lifecycle

`vorbis_block_init()` initializes a `vorbis_block`. In analysis mode, it allocates `vorbis_block_internal` and initializes `PACKETBLOBS` bit buffers. The middle packet blob aliases `vb->opb`; others are separately allocated for bitrate management.

`_vorbis_block_alloc()` provides block-local aligned allocation. If the current local store cannot satisfy a request, it chains the old store for later cleanup and allocates a new one.

`_vorbis_block_ripcord()` frees chained stores, consolidates storage if needed, and resets local allocation state.

`vorbis_block_clear()` clears packet blobs, frees internal analysis data, reaps local allocation, and zeroes the block.

## Shared DSP Initialization

`_vds_shared_init()` initializes common encode/decode DSP state:

- Validates codec setup and block sizes.
- Allocates `private_state`.
- Initializes MDCT transforms for both block sizes.
- Computes window indexes.
- Allocates PCM buffers and return pointers.
- Initializes floor and residue backend lookups.
- For encode: initializes FFT lookups, encode codebooks, psychoacoustic lookups, and sets `analysisp`.
- For decode: initializes decode codebooks and destroys static book params after decode setup.

If decode codebook initialization fails, it cleans up via `vorbis_dsp_clear()`.

## Analysis Side

`vorbis_analysis_init()` calls shared init in encode mode, builds global psychoacoustic state, initializes envelope state, initializes bitrate management, and starts packet sequence numbering after the three Vorbis headers.

`vorbis_analysis_buffer()` returns writable channel buffers at `pcm_current`, expanding PCM storage when needed and freeing cached header packets.

`vorbis_analysis_wrote()` commits input samples or EOF. At EOF it extrapolates trailing samples using LPC where possible and appends several long blocks of padding/extrapolated data. For early stream starts it may reverse-extrapolate the beginning through `_preextrapolate_helper()`.

`vorbis_analysis_blockout()` determines when enough PCM exists for the next block, runs envelope search, sets next window size, classifies block type, copies delayed PCM into block-local storage, updates granule position, shifts the analysis buffer, and returns a ready `vorbis_block`.

## Synthesis Side

`vorbis_synthesis_init()` calls shared init in decode mode and resets synthesis state.

`vorbis_synthesis_restart()` resets decode center/window positions, PCM return state, granule position, sequence number, EOF flag, and backend sample count.

`vorbis_synthesis_blockin()` accepts a decoded block and performs overlap/add into the DSP PCM buffer. It handles all small/large window transitions, accumulates bit accounting, detects sequence holes, tracks granule position, trims extra samples from short final packets, and marks EOF.

`vorbis_synthesis_pcmout()` exposes pending decoded PCM channel pointers.

`vorbis_synthesis_read()` marks samples consumed.

`vorbis_synthesis_lapout()` exposes additional lapping/end-buffer data for vorbisfile use, including buffer unfragmentation when the two-fragment PCM arrangement wraps.

`vorbis_window()` returns the active window table for a block size.

## Cleanup

`vorbis_dsp_clear()` frees envelope state, MDCT transforms, floor/residue lookups, psychoacoustic state, global psy look, bitrate manager state, FFT lookups, PCM buffers, cached headers, and backend state.

## Risks

This file manages complex lifetime and overlap invariants. Key risks are PCM buffer shifting, granule-position correction for corrupt or unusual final packets, local block allocation lifetime, and encode/decode differences in shared initialization.

It includes explicit guards against malicious or corrupt frames that set EOS with a backdated granule position by limiting sample trimming to actually buffered samples.
