# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcmainct.c

Compression main buffer controller between preprocessing and coefficient compression.

Key behavior:
- Maintains per-component downsampled strip buffers for one iMCU row.
- In pass-through mode, repeatedly asks the preprocessor to fill row groups, then hands complete iMCU rows to the coefficient controller.
- Tracks suspension and adjusts the caller's input-row counter so a suspended final input row is not incorrectly treated as consumed.
- Contains dormant full-image buffering code under `FULL_MAIN_BUFFER_SUPPORTED`, but that macro is undefined in this file.
- `jinit_c_main_controller` allocates strip buffers unless raw-data mode bypasses the module.

Dependencies:
- Calls `cinfo->prep->pre_process_data` and `cinfo->coef->compress_data`.
- Uses component dimensions computed by `jcmaster.c`.

Notable risks:
- Full-buffer mode is compiled out, so any request for a full main buffer errors.
- The suspension row-counter adjustment is intentionally subtle and coupled to caller expectations in the public compression API.
