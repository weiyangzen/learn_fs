# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/scf.h

Shared definitions for Ghostscript CCITTFax encoding and decoding filters.

It documents the CCITT Group 3 and Group 4 run-length Huffman scheme and declares the encoding and decoding tables used by the encoder/decoder.

Major contents:

- Maximum safe line width calculation `cfe_max_width` and output-code byte sizing macro.
- Encoding table types and extern declarations for white/black run tables, EOL, uncompressed, 2-D pass/vertical/horizontal, and Group 3 2-D EOL codes.
- Decode node type aliases and negative exceptional values: `run_error`, `run_zeros`, `run_uncompressed`, `run2_pass`, and `run2_horizontal`.
- Initial/minimum decode bit counts for white, black, 2-D, and uncompressed decoding tables.
- Optimized pixel-run detection macros `skip_white_pixels` and `skip_black_pixels`, using byte-run tables and handling `BlackIs1`.

This is image compression support for CCITT fax filters, not filesystem logic.
