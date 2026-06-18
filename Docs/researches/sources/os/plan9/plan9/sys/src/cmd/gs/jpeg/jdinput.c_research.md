# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdinput.c

Purpose: input controller for decompression, coordinating marker parsing and compressed scan consumption.

Key structures and routines:
- `my_input_controller` extends `jpeg_input_controller` with `inheaders`.
- `initial_setup()` validates dimensions, precision, component count, sampling factors, initializes component block/sample dimensions, and determines multi-scan status.
- `per_scan_setup()` computes MCU geometry for single-component and interleaved scans.
- `latch_quant_tables()` saves the quant table actually used by each component’s first scan.
- `start_input_pass()` sets up per-scan MCU geometry, latches quant tables, starts entropy and coefficient controllers, and switches `consume_input` to coefficient consumption.
- `finish_input_pass()` switches `consume_input` back to marker consumption.
- `consume_markers()` reads markers until SOS/EOI/suspension and coordinates first versus later scans.
- `reset_input_controller()` resets stream state and related marker/error/progression state.
- `jinit_input_controller()` allocates and initializes the controller.

Important behavior:
- Separates header/marker consumption from compressed coefficient consumption by swapping the `consume_input` method pointer.
- Supports multi-scan and progressive files by allowing later SOS markers only when expected.
- Quant tables are copied per component so later table-slot reuse does not corrupt final dequantization.
- Initializes transcoder-relevant dimensions even when full decompression master setup is not used.

Dependencies:
- Marker reader, entropy decoder, coefficient controller, JPEG memory manager, and error manager.

Notes:
- This is the central bridge between `jdmarker.c` and entropy/coefficient decoding.
