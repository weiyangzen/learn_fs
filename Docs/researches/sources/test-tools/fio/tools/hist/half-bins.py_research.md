# sources/test-tools/fio/tools/hist/half-bins.py

Purpose: small Python 3 filter that reduces fio histogram log resolution by merging adjacent latency bins. It is intended for `*_clat_hist*` files and writes a compatible lower-bin-count log to stdout.

Important APIs/functions: `main(ctx)` computes `stride = 1 << ctx.coarseness`, opens the input file, preserves the first three comma-separated fields, parses remaining bins as integers, then emits sums over consecutive `stride`-sized groups. CLI arguments are `FILENAME` and `--coarseness/-c`.

Control flow: every input line is split on `", "`, the metadata fields are copied, histogram bins are transformed with a range step of `stride`, and the final group is emitted using the tail slice. There is no streaming generator abstraction; the file is read with `readlines()`.

State/persistence: read-only input file, stdout output, no persistent state. All per-line state is local lists and counters.

Dependencies/integration: only standard Python modules. Output is meant to feed `fiologparser_hist.py`, which auto-detects reduced histogram column counts.

Risks/test signals: assumes exact comma-space separators and integer bins. The loop `range(0, len(hist) - stride, stride)` plus a final tail sum works for typical evenly divisible fio bin counts but should be tested for one-stride, non-divisible, and very short histograms. Memory usage is proportional to file size because of `readlines()`.
