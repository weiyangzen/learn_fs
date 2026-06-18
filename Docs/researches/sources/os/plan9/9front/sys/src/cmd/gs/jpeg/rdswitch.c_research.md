# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/rdswitch.c

Support code for `cjpeg` command-line switches that need parsing beyond simple scalar values.

Main entry points:
- `read_quant_tables` reads one or more 64-entry quantization tables from an ASCII text file and installs them with `jpeg_add_quant_table`.
- `read_scan_script` parses a progressive scan script into `jpeg_scan_info` records when `C_MULTISCAN_FILES_SUPPORTED` is enabled.
- `set_quant_slots` parses `N[,N,...]` and assigns quantization table selectors to components.
- `set_sample_factors` parses `HxV[,HxV,...]` and assigns per-component sampling factors.

Parsing helpers:
- `text_getc` skips `#` comments while preserving newline as a separator.
- `read_text_integer` reads unsigned decimal integers with one trailing terminator.
- `read_scan_integer` normalizes scan-script punctuation so commas/dashes can act as separators while `:` and `;` retain structural meaning.

Important behavior:
- Quantization tables are implicit table numbers 0..`NUM_QUANT_TBLS-1`; too many tables or nonnumeric data are reported on stderr.
- Scan scripts are capped at `MAX_SCANS` 100 and copied into IJG image-pool memory before assigning `cinfo->scan_info`.
- Sampling factors are constrained to 1..4.
- If fewer quant slots are given than components, the final value is replicated; if fewer sampling factors are given, remaining components default to 1x1.

Filesystem relevance:
- Reads small text control files for image encoding. No filesystem internals.
