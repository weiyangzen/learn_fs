# sources/sync-backup/bup/test/int/test_midx.py

Purpose: verifies that `bup midx --check -a` tolerates a missing `.idx` file when a generated `.midx` still covers pack indexes.

Important APIs/types/functions: local wrappers `runc()` and `bupc()`, `bup.path.exe()`, `glob`, `unlink`, and the bup commands `init`, `index`, `save`, and `midx`.

Control flow: initializes a temporary bup repository, saves two sampledata subsets to create multiple pack indexes, forces midx generation, asserts one `.midx` exists and more than one `.idx` exists, deletes one `.idx`, then reruns `midx --check -a`.

State and persistence behavior: writes a real bup repository under `tmpdir`, mutates `GIT_DIR`/`BUP_DIR` in `os.environb`, creates pack index and midx files, and removes one pack index file to simulate partial index loss.

Dependencies/integration points: exercises bup CLI integration with Git pack/index layout and the multi-index verifier. It depends on bundled `test/sampledata` paths and the repository executable returned by `bup.path.exe()`.

Risks and test signals: assumes enough sample data to produce multiple `.idx` files. The only explicit signal after deletion is successful completion of `midx --check -a`; a failure would indicate the checker cannot fall back to the midx or mishandles missing per-pack indexes.
