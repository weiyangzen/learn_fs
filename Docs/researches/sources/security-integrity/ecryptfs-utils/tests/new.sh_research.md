## sources/security-integrity/ecryptfs-utils/tests/new.sh

Purpose: Template script for creating a new eCryptfs test. It contains GPL header boilerplate, author placeholders, standard `test_script_dir` and `rc` setup, sources `etl_funcs.sh`, installs a cleanup trap, and leaves a `# TEST` placeholder.

Important APIs and functions: `test_cleanup`, trap on `0 1 2 3 15`, source of `../lib/etl_funcs.sh`. Control flow is intentionally skeletal: initialize failure status, source helpers, trap cleanup, execute future test body, set `rc=$?`, and exit.

State and persistence: None beyond shell variables unless a future test fills in operations. Dependencies are bash and the test library. Integration role is developer-facing consistency rather than runtime suite execution. Risks are that copied tests may inherit minimal cleanup that does not remove mounts/keys unless authors expand it; the placeholders must be replaced to avoid meaningless tests.
