# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jpegtran.c

Purpose: command-line frontend for lossless JPEG transcoding and optional lossless or mostly-lossless coefficient-domain transformations.

Key contents:
- Includes `cdjpeg.h`, `transupp.h`, and `jversion.h`.
- Global command state: `progname`, `outfilename`, `copyoption`, and `transformoption`.
- `usage()` prints supported switches and exits.
- `select_transform()` enforces at most one image transform.
- `parse_switches()` handles command-line options for marker copying, arithmetic coding, optimization, progressive output, scan scripts, restart intervals, memory limit, output file, debug output, grayscale conversion, and transforms.
- `main()` wires decompressor/compressor objects, file IO, marker copy setup, coefficient reading/writing, transform workspace, transform execution, and cleanup.

Important behavior:
- Performs a dummy switch parse before opening/reading the source, then reparses after `jpeg_copy_critical_parameters()` so destination options apply to initialized compression parameters.
- Reads source image as DCT coefficient arrays with `jpeg_read_coefficients()` and writes with `jpeg_write_coefficients()`.
- Uses `jcopy_markers_setup()` and `jcopy_markers_execute()` to preserve comments or all extra markers depending on `-copy`.
- Transform support is conditional on `TRANSFORMS_SUPPORTED`; unsupported transform requests exit with an error.
- `-progressive` and `-scans` are deferred until enough output context is available.
- Exit status is warning-aware: warning count returns `EXIT_WARNING`, otherwise `EXIT_SUCCESS`.

Dependencies:
- IJG app support (`cdjpeg.h`), transform support (`transupp.h`), libjpeg compression/decompression APIs, stdio helpers such as `read_stdin()` and `write_stdout()`.
