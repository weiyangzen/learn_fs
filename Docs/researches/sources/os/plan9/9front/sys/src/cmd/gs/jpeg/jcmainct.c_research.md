# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcmainct.c

Main buffer controller between preprocessing/downsampling and coefficient compression.

Key points:
- Defines a controller that tracks current iMCU row, row groups received, suspension state, pass mode, and component strip buffers.
- Full-image main buffering is present but disabled with `#undef FULL_MAIN_BUFFER_SUPPORTED`; normal operation uses strip buffers.
- `start_pass_main` installs the simple pass-through processor for non-raw input and returns immediately for raw-data mode.
- `process_data_simple_main` fills one iMCU row via `prep->pre_process_data`, returns for more input when incomplete, sends full rows to `coef->compress_data`, and uses an input-row-counter adjustment to handle output suspension without signaling false image completion.
- `jinit_c_main_controller` skips buffers for raw-data input or allocates per-component strip buffers sized to downsampled DCT block width and iMCU height.

Dependencies and interactions:
- Receives application scanlines from `jpeg_write_scanlines`.
- Drives `jcprepct.c` and `jccoefct.c`.

Risk notes:
- The suspension workaround manipulates `in_row_ctr`; callers must use returned counts exactly.
- Full-buffer modes are not available in this build path despite retained code.
- Raw-data input bypasses this module entirely.
