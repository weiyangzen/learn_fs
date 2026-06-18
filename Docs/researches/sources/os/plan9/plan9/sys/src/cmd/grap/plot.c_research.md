# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/plot.c

This file emits `pic` drawing commands for graph data. It handles line/arrow segments, circles, raw pic passthrough, string plots, numeric plots, and path continuation.

`xyname` converts a `Point` into the proper coordinate macro call and applies log validation/transformation. `numlist` turns bare numeric rows into default plotted points or connected path segments.

`drawdesc` assigns default path style/symbols to an object, and `next` either starts or extends a named line path while updating coordinate ranges.
