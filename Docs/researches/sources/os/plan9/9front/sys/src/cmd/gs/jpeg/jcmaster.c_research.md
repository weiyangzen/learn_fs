# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcmaster.c

Compressor master control: validation, scan setup, and pass scheduling.

Key points:
- `initial_setup` validates image dimensions, component counts, sample precision, sampling factors, scanline width overflow, component block/sample dimensions, and total iMCU rows.
- `validate_script` checks multscan/progressive scan scripts for component order, valid progression parameters, DC-before-AC rules, refinement sequence consistency, and complete data coverage.
- `select_scan_parameters` chooses current scan component list and spectral/successive approximation parameters from `scan_info` or creates a single sequential scan.
- `per_scan_setup` computes MCU geometry for interleaved and noninterleaved scans, MCU membership arrays, last-column/last-row widths, and restart interval derived from rows.
- `prepare_for_pass` orchestrates main input, Huffman optimization, and output passes, starting only the modules needed for the pass and controlling delayed marker output.
- `pass_startup` emits frame and scan headers on first scanline/raw-data call for single-pass compression.
- `finish_pass_master` advances pass type, scan number, and pass number.
- `jinit_c_master_control` allocates master state, validates parameters, determines progressive mode, forces optimized coding for progressive output, and computes total pass count.

Dependencies and interactions:
- Central coordinator for color conversion, downsampling, preprocessing, FDCT, entropy, coefficient, main, and marker modules.
- Used by normal compression and transcoding; `transcode_only` changes the initial pass type.

Risk notes:
- Progressive mode forces Huffman optimization as a compatibility/default-quality choice.
- Many optional modes depend on compile-time gates (`C_MULTISCAN_FILES_SUPPORTED`, `C_PROGRESSIVE_SUPPORTED`, `ENTROPY_OPT_SUPPORTED`).
- Scan script validation is strict; malformed or incomplete scripts fail before output.
