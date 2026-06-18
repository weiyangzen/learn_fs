# sources/sync-backup/bup/test/int/test_repo.py

Purpose: tests repository location normalization for local, remote, and reverse-server modes.

Important APIs/types/functions: `bup.client.Config`, `main_repo_location`, `repo_location_url`, `bup.url.URL`, `os.environb`, `fsencode`, and `devnull`.

Control flow: `test_repo_location_url()` verifies URL passthrough for a URL directly and for a `Config` containing a URL. `test_main_repo_location()` defines helper constructors, temporarily mutates `BUP_SERVER_REVERSE`, and checks default local repository, `host:path` SSH config parsing, invalid remote handling via injected `die`, and reverse server URL construction.

State and persistence behavior: temporarily changes `BUP_SERVER_REVERSE` and restores or removes it in a `finally` block. No repository is created.

Dependencies/integration points: integrates repo-location parsing with URL representation, client configuration, test harness default `GIT_DIR`/`BUP_DIR` behavior from `conftest.py`, and reverse-server environment semantics.

Risks and test signals: environment leakage would affect later tests, so restoration is critical. Signals are structural equality of `URL`/`Config` objects and an expected exception for malformed remote strings.
