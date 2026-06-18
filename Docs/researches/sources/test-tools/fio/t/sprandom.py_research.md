# sources/test-tools/fio/t/sprandom.py

Purpose: fio `sprandom` feature tests. It validates accepted sparse-random configurations and expected failures for incompatible random generators, random-map settings, read mode, too many regions, and chunk sizes equal to the whole file.

Important APIs and types: `FioSPrandomTest` extends `FioJobCmdTest`. `SPRANDOM_OPT_LIST` defines options copied from test dictionaries into fio arguments, including `spr_op`, `spr_num_regions`, `spr_cs`, `size`, `norandommap`, `random_generator`, and `rw`.

Control flow: `main()` parses fio path and test filters, creates a timestamped artifact root, builds `test_env`, and runs `TEST_LIST`. `setup()` uses libaio, direct I/O, `iodepth=16`, `sprandom=1`, a fixed filename, and a configurable `bs` parameter, defaulting to `rw=randwrite` if not specified.

State and persistence: it creates or overwrites `sprandom_testfile` in the current working directory via fio and writes fiotestlib artifacts. No explicit cleanup is performed in this script.

Dependencies and integration points: requires Linux/libaio according to the umbrella test requirements, Python, fio sprandom support, fiotestlib, and fiotestcommon success constants. `run-fio-tests.py` registers it as executable test 1019.

Risks and test signals: the script checks process success/failure rather than distribution quality. The fixed filename can collide with concurrent runs in the same directory. Success signals are the expected exit status for each valid or invalid option combination.
