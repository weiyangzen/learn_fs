# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/stats.c

`stats.c` defines the Venti runtime stats table, global counters, history ring, and histogram/binning helper. `statsinit()` allocates a 90,000-sample history and starts a sampler that copies `stats` once per second.

`setstat()`, `addstat()`, and `addstat2()` update counters under `statslock`, with `collectstats` allowing increments to be disabled. `binstats()` converts a time range into graph bins by applying a caller-supplied function to consecutive `Stats` samples.

The stat descriptions must stay aligned with `dat.h:/NStat`; web graphing and status pages rely on these names and counter indices.
