# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdswitch.c

Helper parser for advanced `cjpeg` command-line switches.

Handled switch families:

- `-qtables file`: `read_quant_tables()` reads one or more 64-entry decimal quantization tables from comment-capable text and installs them with `jpeg_add_quant_table()`.
- `-scans file`: under `C_MULTISCAN_FILES_SUPPORTED`, `read_scan_script()` parses up to 100 scan definitions, including optional progressive JPEG parameters `Ss Se Ah Al`, then stores a `jpeg_scan_info` array in `cinfo`.
- `-qslots N[,N,...]`: `set_quant_slots()` assigns per-component quantization table selectors, replicating the last supplied value.
- `-sample HxV[,HxV,...]`: `set_sample_factors()` assigns per-component horizontal/vertical sampling factors, defaulting the rest to `1x1`.

Internal parsing uses `text_getc()` to skip `#` comments and `read_text_integer()` / `read_scan_integer()` to read decimal numbers plus punctuation. Errors are reported to `stderr` and returned as `FALSE` rather than through libjpeg fatal exits. The file mutates compressor setup state but performs no image I/O itself.
