# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_spacetime

## Purpose

This Munin plugin estimates days until storage exhaustion by fetching remote RRD files, summing disk-free data, extrapolating recent growth, and writing a JSON sidecar for web use.

## Important APIs, Types, and Functions

Constants define a Munin host, RRD filenames, local paths, and `WEBFILE`. `rsync_rrd` copies remote RRDs. `format_time` formats timestamps. `predict_future(past_s)` uses `rrdtool.fetch` to compute average start/end disk usage and remaining days. `write_to_file(samples)` atomically writes JSON-like output.

## Control Flow

Config mode prints two series. Normal mode currently does not call `rsync_rrd`; it predicts four-week and two-week remaining days from local RRDs, prints values when available, and writes available samples to `/var/www/tahoe/spacetime.json`.

## State, Dependencies, Integration, Risks, and Tests

Persistent state is `WEBFILE` and local RRD reads. Dependencies are `rrdtool`, rsync if enabled, hard-coded production RRD paths, and Munin. Risks include hard-coded infrastructure, `os.system` shell command construction, assertions for rsync failures, assuming the fourth-from-last RRD point is valid, and writing non-general JSON manually. Tests should mock `rrdtool.fetch`, cover None data paths, positive/negative growth, and atomic write content.
