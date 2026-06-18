# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jccoefct.c

Compression coefficient buffer controller: top-level bridge between forward DCT/quantization and entropy encoding.

Key behavior:
- Enables full-image coefficient buffering when entropy optimization or compressor multiscan support is compiled.
- Defines private `my_coef_controller` containing public controller methods, iMCU row counters, current MCU counters, a per-MCU block pointer buffer, and optional per-component virtual coefficient arrays.
- `start_iMCU_row` initializes row counters differently for interleaved and noninterleaved scans, with bottom-image handling.
- `start_pass_coef` selects pass behavior: single pass-through, first save-and-pass pass, or later output-only pass.
- `compress_data` handles single-pass compression: builds MCU block lists from source sample planes, runs forward DCT, creates dummy right-edge and bottom-edge blocks with DC values chosen for compact entropy coding, calls entropy `encode_mcu`, and preserves counters on suspension.
- `compress_first_pass` handles multipass first pass: DCTs all components into virtual block arrays, pads right and bottom edges, then emits the current strip through `compress_output`.
- `compress_output` reads MCU block pointers from virtual arrays for the current scan and feeds entropy coding, preserving counters on suspension.
- `jinit_c_coef_controller` allocates the controller, installs `start_pass`, and either allocates full-image virtual arrays padded to sampling factors or a single-MCU large buffer.

Dependencies:
- Internal IJG compressor types and services from `jinclude.h` and `jpeglib.h`.
- Uses memory manager allocation/virtual-array APIs, forward DCT module, entropy encoder, component geometry, and buffer-mode enums.

Research notes:
- Suspension support is stateful: `mcu_ctr` and `MCU_vert_offset` are saved so encoding can resume.
- In single-pass suspension, the current MCU may be re-DCTed on retry.
- Dummy block DC replication at image edges is an intentional compression-size optimization.
- Full coefficient buffering is required for optimized Huffman coding and multiscan/progressive-style output paths.
