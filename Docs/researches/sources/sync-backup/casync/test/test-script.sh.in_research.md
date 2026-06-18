# sources/sync-backup/casync/test/test-script.sh.in

Purpose: comprehensive end-to-end CLI integration test for casync archives, indexes, extraction, seeking, SSH remoting, and HTTP remoting across digest/compression variants.

Important APIs/types/functions: invokes `casync list`, `mtree`, `digest`, `make`, `extract`, remote locators, `test-calc-digest`, `notify-wait`, `pseudo-ssh`, and `http-server.py`. It compares outputs with `diff -q` and filesystem trees with `diff -ur --no-dereference`.

Control flow/state: creates scratch source tree from `test-files` and `src`, generates `.catar` and `.caidx`, verifies list/mtree/digest equivalence, extracts with/without seeds and hardlinks, tests path seeking into archives, serves remote paths over pseudo SSH and HTTP, then cleans scratch state.

Dependencies/integration: central CLI regression lane; depends on configured compressor libraries, builddir substitutions, shell tools, Python HTTP helper, and local filesystem semantics.

Risks/test signals: broad but environment-sensitive. It can miss metadata unsupported by the current user/filesystem, but it is the strongest single signal for cross-module behavior.

Source research group: `subset-b-009122`.
