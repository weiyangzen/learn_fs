<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/815 -->
# sources/test-tools/xfstests/tests/xfs/815

Purpose: races fsstress against metadata-directory path scrub operations to catch crashes, livelocks, or metapath lookup corruption under load.

Important APIs, types, and functions: probes `xfs_io -x -c 'scrub metapath ...'` through `try_verb`, discovers supported verbs (`quotadir`, quota roots, `rtdir`, `rtbitmap`, `rtsummary`, `rtrmapbt`, `rtrefcbt`), and runs `_scratch_xfs_stress_scrub`.

Control flow: after mkfs and mount, the script sources mkfs geometry from filtered output, builds a list of supported metapath scrub commands including realtime group numbers, and feeds them to the stress scrub helper.

State and persistence behavior: scratch filesystem contents mutate under fsstress. The discovered verb list is logged to `$seqres.full`; cleanup stops the stress scrub worker.

Dependencies and integration points: depends on xfs_io metapath scrub support, scratch XFS, realtime-group geometry when available, and xfstests inject/fuzzy/xfs helpers.

Risks and test signals: skips if no metapath verbs are accepted. Success is a quiet stress run ending in `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/815 -->
