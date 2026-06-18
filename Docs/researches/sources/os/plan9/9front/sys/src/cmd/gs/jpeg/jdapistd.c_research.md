# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdapistd.c

Standard decompression API for full pixel output.

Key points:
- `jpeg_start_decompress` requires header-ready state, initializes decompressor master modules, handles buffered-image mode, preloads all scans for multscan files when needed, and performs dummy output passes before entering scanning/raw-output state.
- `output_pass_setup` prepares an output pass, runs any two-pass color-quantization dummy passes, and transitions to `DSTATE_SCANNING` or `DSTATE_RAW_OK`.
- `jpeg_read_scanlines` validates state, warns on excess calls, updates progress, invokes the main decompressor controller, and advances `output_scanline`.
- `jpeg_read_raw_data` validates raw-output state, requires one full iMCU row of caller buffer space, invokes coefficient decompression directly, and advances `output_scanline`.
- Buffered-image APIs `jpeg_start_output` and `jpeg_finish_output` select output scan numbers, run output pass setup/finish, and consume input until enough scans are available.

Dependencies and interactions:
- Pulling this file into an application links the full decompressor.
- Uses decompressor master, input controller, coefficient controller, and main controller modules outside this group.

Risk notes:
- Multiscan input preload and buffered-image APIs require `D_MULTISCAN_FILES_SUPPORTED`.
- Dummy passes require `QUANT_2PASS_SUPPORTED`.
- Raw-data output buffer height must match the computed iMCU row height.
