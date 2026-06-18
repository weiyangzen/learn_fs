# sources/distributed-fs/tahoe-lafs/misc/simulators/storage-overhead.py

## Purpose

This standalone simulator estimates Tahoe-LAFS immutable-file storage overhead for a given file size. It reports URI length, one-share allocated size, total allocated share space across all shares, ideal expansion, and effective expansion. It is an operational/modeling helper rather than production node code.

## Important APIs, Types, And Functions

`roundup(size, blocksize=4096)` rounds share allocations to disk blocks. `BigFakeString` is a seek/tell-only fake file object used to satisfy uploader encoder setup without holding real data. `calc(filesize, params=(3,7,10), segsize=DEFAULT_IMMUTABLE_MAX_SEGMENT_SIZE)` is the main API; it switches between literal-file URI accounting and CHK share accounting. `main()` prints one calculation from `sys.argv[1]`, and `chart()` emits CSV-like rows for geometrically increasing file sizes.

## Control Flow

The script parses the first command-line argument. If it is `chart`, `chart()` loops from size 2 to under 1 MiB, calling `calc()` and printing expansion. Otherwise `main()` converts the argument to an integer, calls `calc()`, and prints human-readable fields. In `calc()`, files at or below `upload.Uploader.URI_LIT_SIZE_THRESHOLD` are represented as literal URIs with no shares. Larger files instantiate `upload.FileUploader`, configure erasure-coding parameters, install the fake file handle and a fixed encryption key, run encoder setup, and then compute share allocation metadata and URI size.

## State And Persistence

The file owns no persistent state. It mutates only the fake file pointer in `BigFakeString`, the local `FileUploader`, and command-line output. It uses fixed dummy key/storage-index bytes for sizing, not for security.

## Dependencies And Integration Points

It depends on `allmydata.uri`, `allmydata.storage`, `allmydata.immutable.upload`, `DEFAULT_IMMUTABLE_MAX_SEGMENT_SIZE`, and `mathutil`. The constants and uploader behavior tie the simulator to Tahoe-LAFS immutable upload internals and share layout assumptions.

## Risks

The simulator reaches into upload internals (`FileUploader(None)`, `set_filehandle`, `setup_encoder`) and comments that this was changed, so it can drift when uploader APIs or share layout change. The extension size is hard-coded as 429 bytes, making the output stale if URI extension serialization changes. `sys.argv[1]` is accessed unconditionally, so missing arguments raise `IndexError`.

## Test Signals

Useful checks are running the script for small literal sizes, boundary sizes around `URI_LIT_SIZE_THRESHOLD`, large files across segment boundaries, and `chart` output. Regression tests should compare monotonicity and known expansion values after changes to immutable upload layout.
