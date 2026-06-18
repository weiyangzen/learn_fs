# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/coord.c

This file manages `grap` coordinate systems. It tracks default/current coordinate names, explicit x/y ranges, log-scale flags, and resets graph margins when explicit coordinates are supplied.

`coord` applies pending x/y ranges to an `Obj`, validates positive lower bounds for log axes, records log flags, and disables automatic x numbering. Repeated implicit default coordinate definitions rename the default to `gg<N>` to avoid collision.

`resetcoord` changes the current coordinate object used by later points.
