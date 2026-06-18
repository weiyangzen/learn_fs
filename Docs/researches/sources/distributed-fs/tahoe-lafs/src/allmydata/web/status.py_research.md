# sources/distributed-fs/tahoe-lafs/src/allmydata/web/status.py

## Purpose
Renders operation status pages and machine-readable status/statistics for uploads, downloads, mutable publishes/retrieves, servermap updates, helper state, and node counters. It also produces download event JSON for frontend timing visualizations and OpenMetrics output for statistics scraping.

## Important APIs, Types, And Functions
`UploadResultsRendererMixin` renders upload result timings, rates, shares, and server maps. Page/element pairs include `UploadStatusPage`/`UploadStatusElement`, `DownloadStatusPage`/`DownloadStatusElement`, `RetrieveStatusPage`/`RetrieveStatusElement`, `PublishStatusPage`/`PublishStatusElement`, and `MapupdateStatusPage`/`MapupdateStatusElement`. `_EventJson`, `_find_overlap`, `_find_overlap_requests`, and `_color` support download event visualization. `marshal_json`, `Status`, and `StatusElement` summarize active/recent operations. `HelperStatus`, `HelperStatusElement`, `Statistics`, and `StatisticsElement` render helper and stats pages; `Statistics.render_OPENMETRICS` emits OpenMetrics text.

## Control Flow
`Status.render_HTML` builds active/recent operation lists from the history object; `render_JSON` serializes them with `marshal_json`. `Status.getChild` parses paths like `up-1`, `down-2`, `publish-3`, `retrieve-4`, and `mapupdate-5`, then searches the corresponding history lists for a matching counter and returns the detail page. Detail elements read status objects synchronously or with Deferred upload results. Download status installs child `event_json` for timeline data. `Statistics` dispatches `t=openmetrics` through `MultiFormatResource` and mangles Tahoe stat names into metric identifiers/quantile labels.

## State And Persistence
This module owns no durable state. It reads live and recent operation status objects from a history provider, helper stats from the helper service, and counters/stats from a stats provider. `_EventJson` and detail elements hold references to status objects. The only transformation state is request-local rows, colors, and JSON dicts.

## Dependencies And Integration Points
It depends on Twisted templates/resources, Tahoe status interfaces (`IUploadStatus`, `IDownloadStatus`, `IPublishStatus`, `IRetrieveStatus`, `IServermapUpdaterStatus`), base32/idlib/json utilities, and formatting helpers from `common.py`. It is mounted by `root.Root` at `/status`, `/statistics`, and dynamic `/helper_status`; `unlinked.UploadResultsElement` reuses `UploadResultsRendererMixin`. Tests include `src/allmydata/test/web/test_status.py`, `test_openmetrics.py`, `test_statistics.py`, `test_storage_web.py` for adjacent stats patterns, and WebAPI integration coverage.

## Risks And Test Signals
Risks include many loosely typed status-object method assumptions, bytes/str mismatches in storage-index rendering, `Status.getChild` returning `None` for unknown counters instead of an explicit error resource, download result renderers depending on `get_results()` despite a comment noting it is unimplemented, and OpenMetrics name mangling that may not cover all metric characters. Tests should cover active/recent sorting, all detail child types, upload result Deferreds, event JSON shape and row allocation, helper absent/present states, OpenMetrics content type and EOF, NaN handling for `None`, and status JSON fields for all interface types.
