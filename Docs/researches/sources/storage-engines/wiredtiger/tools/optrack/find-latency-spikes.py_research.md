# sources/storage-engines/wiredtiger/tools/optrack/find-latency-spikes.py

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/optrack/find-latency-spikes.py -->
## sources/storage-engines/wiredtiger/tools/optrack/find-latency-spikes.py

### Purpose
`find-latency-spikes.py` visualizes WiredTiger operation tracking text logs, finding function-duration outliers and generating Bokeh HTML dashboards. It creates per-function outlier histograms and bucketed cross-file timeline views.

### Important APIs, Types, and Functions
Global state tracks colors, first/last timestamps, user thresholds, per-file DataFrames, per-function DataFrames, and output dimensions. `initColorList` and `getColorForFunction` assign stable colors. `getIntervalData`, `createCallstackSeries`, and `assignStackDepths` pair begin/end records into intervals with stack depth and duration. Plot functions include `plotOutlierHistogram`, `generateBucketChartForFile`, `createLegendFigure`, `generateNavigatorFigure`, and `generateCrossFilePlotsForBucket`. `generateTSSlicesForBuckets` parallelizes bucket page generation. `parseConfigFile` reads time unit and threshold configuration. `processFile` reads logs and populates DataFrames. `main` wires CLI parsing, processing, plotting, and final output.

### Control Flow
The script validates input and open-file limits, sets job parallelism, initializes colors, optionally parses a config, creates `BUCKET-FILES`, processes each input log into interval DataFrames, normalizes timestamps, generates cross-file bucket HTML files in parallel, then creates `WT-outliers.html` containing outlier histograms that link into bucket pages.

### State and Persistence
Persistent output includes `WT-outliers.html`, `BUCKET-FILES/bucket-*.html`, optional `*-clean.txt` logs, and per-input hidden error logs such as `.filename.log`. In-memory state is heavily global and accumulates across all inputs.

### Dependencies and Integration Points
Depends on pandas, NumPy, Bokeh, multiprocessing, subprocess, and text logs produced by `wt_optrack_decode.py`. It assumes each input row has event type, function, and timestamp, with an optional first line containing seconds since epoch.

### Risks and Test Signals
The script uses older Bokeh APIs (`plot_width`, `TapTool.callback`, `LabelSet render_mode`) that may break on newer Bokeh versions. Several bugs are visible: a malformed string concatenation in timestamp parse error handling, `numOutliers = bucketDF.size` counts cells rather than rows, `threshold = -units` for `stdev` assigns a string-negation error path, and `timeUnitsPerBucket` can be zero when the trace duration is shorter than the bucket count. Global state makes repeated in-process invocation unsafe. Tests should cover malformed begin/end stacks, config parsing, short traces, empty function DataFrames, Bokeh output generation with the pinned dependency version, and multiprocessing bucket generation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/optrack/find-latency-spikes.py -->
