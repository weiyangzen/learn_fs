# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/get-check-failures.sed

Purpose: sed script used during shutdown to extract per-test failure blocks from `runtests.log`.

Important behavior: invoked as `sed -n -f /usr/local/lib/get-check-failures.sed < /results/runtests.log` by `gce-shutdown`. The script is intentionally tiny and acts as part of the failure summary pipeline.

State and dependencies: no state; depends on xfstests log markers such as `BEGIN`, `END`, and failure output shapes.

Integration points: feeds `/results/failures`, which is included in result tarballs and email summaries.

Risks and test signals: if xfstests log format changes, failure extraction can miss relevant context. Regression tests should run the sed script against representative passing, failing, and interrupted logs.
