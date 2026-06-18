# sources/test-tools/fio/tools/genfio

## Purpose
`genfio` is a Bash generator for fio job files that benchmark selected disks/files across block sizes, read/write modes, sequential scheduling, parallel scheduling, or both.

## Important APIs, Types, and Functions
`show_help()` documents options. `gen_template()` writes the `[global]` section to a temporary file; `finish_template()` appends iodepth, runtime/time_based, and direct I/O controls. `diskname_to_printable()` normalizes disk paths for names. `gen_seq_suite()` and `gen_para_suite()` append fio job sections for one disk/mode/block-size in sequential or parallel form, including bandwidth and IOPS log filenames. `gen_fio()` dispatches by selected mode. `parse_cmdline()` handles disks, block sizes, runtime, modes, prefix, file size, iodepth, cached I/O, pre/post commands, and output filename. `check_mode_order()` warns when reads precede writes.

## Control Flow and State
Global variables hold generator configuration, ETA, output path, and temporary template path. Main flow creates the template, parses CLI, finalizes defaults, warns about mode order, copies the template to the output file, appends generated jobs for each block size, and prints ETA.

## Dependencies and Integration Points
It depends on Bash, `mktemp`, `hostname`, `basename`, `sed`, `cp`, and fio job-file syntax. Generated jobs use `ioengine=libaio`, `invalidate=1`, `ramp_time=5`, optional `direct=1`, and `write_*_log` options.

## Risks and Test Signals
Risks include unquoted shell expansions around disk paths/prefixes, destructive benchmarking if disks are raw devices, limited validation of runtime/block/mode inputs, and generated read tests before data exists. Signals are generated `.fio` file content, ETA output, and warning delay when mode order is suspicious.
