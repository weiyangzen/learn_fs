# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/tojpg.c

Command-line JPEG converter. It reads a Plan 9 image from stdin or one file, converts to multi-channel `Memimage` form with `memmultichan`, and writes JPEG using `memwritejpg`.

Options include `-c` comment, `-k` grayscale output, and `-s` alternate/scaled quantization path passed to the JPEG writer. Output is written to stdout through a `Biobuf`.

The command itself is thin; format-specific encoding lives in `writejpg.c`.
