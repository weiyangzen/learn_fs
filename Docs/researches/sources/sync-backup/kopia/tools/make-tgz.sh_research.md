# sources/sync-backup/kopia/tools/make-tgz.sh

Purpose: packages a Kopia binary plus `LICENSE` and `README.md` into a gzip-compressed tarball with a versioned top-level directory.

Control flow/APIs: positional args are output directory, base filename, and binary path. It creates a temp directory, stages `$basefname`, copies the binary and project metadata into it, runs `tar -C $temp_dir -cvz $basefname > $output_dir/$basefname.tar.gz`, then removes the temp directory.

State/persistence: writes exactly one archive under the output directory and creates/removes one temporary staging tree. Archive contents are rooted at `$basefname`.

Dependencies/integration: requires POSIX shell, `mktemp`, `cp`, and `tar`. It is used by release packaging to produce tar artifacts consumed by publishing scripts and package managers.

Risks/test signals: arguments are mostly unquoted, so paths with spaces can break. Cleanup is not trap-protected, leaving temporary directories on failure. It assumes `LICENSE` and `README.md` exist in the current working directory. Release packaging success is the practical test signal.
