# sources/distributed-fs/tahoe-lafs/src/allmydata/web/check_results.py

## Purpose
Renders check, verify, repair, deep-check, and deep-check-and-repair results for the Tahoe-LAFS WebAPI. It converts `ICheckResults` and `ICheckAndRepairResults` objects into HTML template elements or JSON, and it lets deep operation result pages drill into per-storage-index details through the `/operations/<handle>/<storage-index>` child path.

## Important APIs, Types, And Functions
The JSON helpers are `json_check_counts`, `json_check_results`, and `json_check_and_repair_results`. `ResultsBase` provides shared HTML rendering for share counts, corrupt shares, share maps, and permuted server order. `LiteralCheckResultsRenderer`, `CheckResultsRenderer`, and `CheckAndRepairResultsRenderer` are `MultiFormatResource` adapters for literal files, normal checks, and repair checks. `DeepCheckResultsRenderer` and `DeepCheckAndRepairResultsRenderer` wrap monitor-backed long-running results; their element classes render counters, corrupt-share tables, object lists, and reload/cancel controls inherited from `ReloadMixin`.

## Control Flow
Callers in `filenode.py` and `directory.py` run node `check`, `check_and_repair`, `start_deep_check`, or `start_deep_check_and_repair`, then instantiate one of these renderers. `MultiFormatResource` dispatches `output=json` to JSON renderers and otherwise renders Twisted templates such as `check-results.xhtml`, `check-and-repair-results.xhtml`, `deep-check-results.xhtml`, and `deep-check-and-repair-results.xhtml`. Deep renderers read counters and object maps from `monitor.get_status()`. Their `getChild` decodes the child segment as base32 storage index, looks up the per-object result in the monitor status, and returns a single-object renderer or a `WebError` for unknown storage indexes.

## State And Persistence
The module owns no persistent storage. Renderers keep references to the client, a result object, or a monitor. Long-lived state is in the monitor registered by `operations.OphandleTable`; this file only reads it. Generated JSON includes storage indexes, summaries, health/recoverability, share counts, server long names, corrupt share coordinates, operation completion state, and stats from result objects.

## Dependencies And Integration Points
This module depends on Twisted Web templates, `allmydata.interfaces.ICheckResults` and `ICheckAndRepairResults`, `allmydata.util.base32`, `dictutil.DictOfSets`, Tahoe JSON byte support, and shared web helpers from `common.py`. It is directly integrated by file and directory POST `t=check`, deep-check operation handles, streaming deep-check output in `directory.py`, and the `MoreInfo` check forms in `info.py`. It also uses the client storage broker to present share placement in permuted server order.

## Risks And Test Signals
Important risks are drift between result-interface methods and JSON field names, HTML escaping around paths/summaries/server names, and incomplete deep-repair rendering: `post_repair_corrupt_shares` is explicitly unimplemented and deep check-and-repair JSON sets `count-corrupt-shares-post-repair` from the pre-repair counter. Literal files are handled by `None` results and need separate coverage. Useful test signals exist in `src/allmydata/test/test_checker.py`, `test_deepcheck.py`, and WebAPI integration tests for `start-deep-check`, JSON output, per-SI child resources, repair summaries, and corrupt-share tables.
