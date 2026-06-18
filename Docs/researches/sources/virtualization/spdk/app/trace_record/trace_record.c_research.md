# File Research: sources/virtualization/spdk/app/trace_record/trace_record.c

This file implements `spdk_trace_record`, a recorder that copies trace entries from a running SPDK process's trace shared-memory object into a persistent aggregate trace file. It is complementary to `spdk_trace`: this program records, while `spdk_trace` displays/parses.

The main context is `struct aggr_trace_record_ctx`, which holds the output path, output fd, shared-memory fd, mapped trace file, and one `lcore_trace_record_ctx` per SPDK lcore. Each lcore context tracks a temporary per-lcore file path/fd, whether that lcore has trace history, input/output history headers, the next recorded entry index, first/last TSC values, and total copied entries.

`input_trace_file_mmap()` opens the trace shm object read-only, maps the header first to obtain TSC rate and total trace file size, remaps the entire trace file, and populates lcore contexts with per-lcore histories via `spdk_get_per_lcore_history()`. It rejects zero TSC rate and prints per-lcore entry counts when verbose mode is enabled.

The recorder writes to temporary per-lcore files first. `output_trace_files_prepare()` derives paths as `<aggregate_path>-<lcore>`, unlinks any existing aggregate and temp files, creates temp files for valid lcores, and allocates output history headers sized for each lcore's tracepoint count. `output_trace_files_finish()` frees those headers, closes temp fds, and unlinks temp files.

The hard part is copying from a circular trace buffer without losing order. `lcore_trace_record()` compares shared-memory `next_entry` with the last recorded index, uses a memory read barrier after observing `next_entry`, and appends either a contiguous segment, a wraparound segment, or the full circular buffer into the lcore temp file. It detects rollback, reports missed entries if producers advanced by more than the buffer size, updates copied entry counts, copies tracepoint counters into the output history header, records first/last TSC, and advances `rec_next_entry`.

`trace_files_aggregate()` creates the final trace file. It copies the original trace header and non-lcore sections, recalculates total file size and lcore offsets based on recorded entry counts, writes a new lcore-offsets section, then appends each valid lcore's output history header and copied trace entries from its temp file. It verifies temp-file byte count against `num_entries * sizeof(struct spdk_trace_entry)` and reports the aggregate output path.

The command line requires `-f` output file, `-s` app name, and either `-i` shm ID or `-p` PID. `-q` disables verbose logging, `-t` sets a recording duration in seconds, and `-h` prints usage. The program installs SIGINT and SIGTERM handlers that set `g_shutdown`, records until stopped or until duration expires, aggregates, prints a per-lcore summary in microseconds, unmaps/cleans up, and exits.

Notable caveats:

- `cont_write()` and `cont_read()` use `int` for byte counts derived from `size_t`; in this file their callers pass bounded chunk sizes or structure sizes, but the helper signatures are narrower than the POSIX types.
- Temp files are created with `O_EXCL` after the cleanup pass, so unexpected stale files that cannot be unlinked fail preparation.
- The recorder tolerates missed trace entries by copying the current full circular buffer and reporting the loss; it cannot reconstruct overwritten entries.
