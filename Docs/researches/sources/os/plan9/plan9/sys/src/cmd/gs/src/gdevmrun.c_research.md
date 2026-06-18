# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmrun.c

Experimental run-length encoded memory-device wrapper.

- File explicitly warns that the code has not been tested.
- Represents each scan line as a doubly linked list of runs stored inside the memory device scan-line storage.
- Uses dummy start/end runs, bounded run indices, and bounded run lengths; caps the number of runs per line to avoid stack expansion costs and low compression value.
- `gdev_run_from_mem` copies a memory device into `gx_device_run`, checks whether enough run slots fit per scan line, initializes uninitialized lines to device white, and replaces drawing/get-bits procs.
- Non-fill operations standardize affected lines to normal bitmap form, then call the saved original memory-device procedure.
- `run_expand` converts one run-encoded line to bitmap form using saved `fill_rectangle`.
- `run_standardize` manages the range of lines already converted to standard form.
- `run_line_initialize` builds initial runs and a free list for a line that is first written with a non-white color.
- `run_fill_interval` performs the core run-list edit: finds affected runs, splits preserved prefixes/suffixes, deletes overwritten runs, and inserts/merges new runs.
- `run_fill_rectangle` keeps all-white uninitialized regions cheap, delegates overlapping standardized regions, and converts a line to standard form if it runs out of run slots.
- Risk notes: untested, mutates scan-line storage between two representations, and uses stack arrays sized by `MAX_RUNS`; safest interpretation is an experimental optimization layer for fill-heavy pages.
