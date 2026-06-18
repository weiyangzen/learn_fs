# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdinput.c

Decompressor input controller for marker consumption, scan setup, and compressed-data pass transitions.

Key points:
- `initial_setup` validates dimensions, precision, component count, and sampling factors, then computes component block/sample dimensions and total iMCU rows.
- Detects whether the file has multiple scans based on first scan component count or progressive mode.
- `per_scan_setup` computes MCU geometry for interleaved and noninterleaved scans, including last-column/row dummy-block dimensions and MCU membership.
- `latch_quant_tables` copies each component's active quantization table at its first scan, protecting later output from table slot reuse between scans.
- `start_input_pass` prepares scan geometry, latches quant tables, starts entropy and coefficient input controllers, and switches `consume_input` to coefficient consumption.
- `consume_markers` drives marker reading until SOS/EOI, performs first-SOS setup, starts later scans, and handles tables-only datastreams.
- `reset_input_controller` resets error/marker/progression state for a new datastream.

Dependencies and interactions:
- Marker byte parsing is in `jdmarker.c`; entropy/coefficient scan consumers are initialized here.
- `jdtrans.c` relies on initial DCT sizing done here because it bypasses full `jdmaster.c`.

Risk notes:
- Precision must exactly match the compiled `BITS_IN_JSAMPLE`.
- Multiple scans are not expected unless detected up front; unexpected later SOS in single-scan mode is fatal.
- Quant table mutation after a component's first scan is ignored by design, matching JPEG scan semantics.
