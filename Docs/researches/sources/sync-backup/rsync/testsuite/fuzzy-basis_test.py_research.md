## sources/sync-backup/rsync/testsuite/fuzzy-basis_test.py

Purpose: verifies `--fuzzy` candidate scoring chooses the closest same-directory basis by name similarity, not merely that the final file contents match.

Important APIs and control flow: builds a deep source file `d1/d2/archive-v2.tar` and destination candidates `archive-v1.tar`, `archive-old.tar`, and `unrelated.dat`. It runs `rsync -a --fuzzy --no-whole-file --debug=FUZZY`, then requires debug output naming `archive-v1.tar` as the selected basis before comparing final bytes.

State and dependencies: uses `make_data_file`, direct byte writes for candidate contents, and `run_rsync(capture_output=True)`.

Integration points: exercises generator fuzzy-basis selection and delta basis lookup at depth.

Risks and test signals: the debug-line assertion is the crucial signal because a full transfer could also produce correct bytes. Risk is debug message wording drift.
