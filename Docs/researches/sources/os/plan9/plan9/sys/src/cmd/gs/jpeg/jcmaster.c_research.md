# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcmaster.c

Master control logic for JPEG compression.

Key behavior:
- Validates image dimensions, component counts, sample precision, sampling factors, and scanline width overflow.
- Computes per-component block/sample dimensions and total iMCU rows.
- Validates optional scan scripts, including sequential/progressive consistency, component ordering, DC-before-AC requirements, and successive approximation ordering.
- Selects current scan parameters and computes MCU layout for interleaved and noninterleaved scans.
- Converts restart rows into restart MCU intervals with 16-bit limiting.
- Schedules pass types: main pass, optional Huffman optimization pass, and output pass.
- Coordinates per-pass startup across color conversion, downsampling, preprocessing, FDCT, entropy, coefficient, main, and marker modules.
- Initializes different first-pass behavior for full compression versus coefficient transcoding.

Dependencies:
- Relies on component tables populated by `jcparam.c`, marker writing from `jcmarker.c`, entropy encoders, coefficient controller, and preprocessing/FDCT modules.

Notable risks:
- Progressive mode forces Huffman optimization by default because standard tables are assumed inadequate.
- Compile-time feature macros gate multiscan/progressive/entropy optimization paths.
- Scan-script validation is central; invalid scripts fail before data output.
