# sources/test-tools/fio/tools/fiograph/fiograph.conf

## Purpose
`fiograph.conf` configures colors, labels, styles, and ioengine-specific option lists for the `fiograph.py` fio-job visualization tool.

## Important APIs, Types, and Functions
The `[fio_jobs]` section defines Graphviz HTML label templates, colors, box shape/style, cluster style, and title/item formatting. Sections such as `[exec_prerun]`, `[exec_postrun]`, `[numjobs]`, and `[ioengine]` override colors or display formats. Numerous `[ioengine_*]` sections list engine-specific options that should be highlighted near the ioengine line rather than treated as generic job options.

## Control Flow and State
This is declarative configuration parsed by `configparser.RawConfigParser`. Whitespace-separated `specific_options` values are split by `fiograph.py`.

## Dependencies and Integration Points
It is tightly coupled to `fiograph.py` option lookup names and to fio ioengine option names. It also embeds Graphviz HTML-like label syntax, so malformed templates can break rendering.

## Risks and Test Signals
Risks include stale ioengine option lists as fio evolves, double spaces creating empty option names, Graphviz HTML syntax errors, and color/style assumptions. Signals are visual output from `fiograph.py`, absence of config lookup failures, and correct highlighting of engine-specific options.
