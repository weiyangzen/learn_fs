# sources/test-tools/stress-ng/stress-filename.c

Purpose: implements `filename`, a filename length/character-set stressor that probes or selects allowable filename bytes and repeatedly creates, stats, readdir-validates, and unlinks names of boundary and random lengths.

Important APIs/types/functions: `filename_opts[]` selects probe, POSIX, ext, UTF-8, and UTF-8-like modes. `allowed[256]` stores allowed byte values. `stress_filename_probe_length()` discovers effective max filename length; `stress_filename_probe()` discovers usable bytes by trying `creat()`. `stress_filename_generate_*()` creates repeated, random, valid UTF-8, or deliberately UTF-8-like names. `stress_filename_readdir()` verifies directory enumeration returns exactly the created file and checks stat identity. `stress_filename_test_normal()` and `_utf8()` perform create/stat/fdinfo/unlink checks.

Control flow: the parent creates a temp directory, reads `statvfs().f_namemax`, probes max length and allowed chars, synchronizes, then forks a worker child. The child loops through single-byte, max length, max-1, max+1 expected-fail, increasing length, and random length cases, alternating deterministic and random generated names, while periodically probing `pathconf()`. The parent waits, handles possible OOM SIGKILL restart policy, and tidies the directory.

State and persistence behavior: uses one temporary directory and transient test files. The global `allowed` table is process-local. Cleanup enumerates and unlinks residual entries before removing the directory.

Dependencies and integration points: uses stress-ng temp-dir, fdinfo, OOM adjustment, signal, scheduler, stat wrappers, filename-dot helpers, and option parsing. Registered as `CLASS_FILESYSTEM | CLASS_OS`, `VERIFY_ALWAYS`.

Risks: filename validity differs by filesystem, OS, locale, encoding translation, and compatibility layers. UTF-8-like mode intentionally generates invalid byte sequences. `stress_filename_probe()` has a complex errno condition that may not classify every platform's invalid-name errors cleanly. Readdir name mismatch is informational when stat identity proves the same file, acknowledging non-bijective filename encodings.

Test signals: run all `--filename-opts` modes on ext4, tmpfs, btrfs, Cygwin/WSL-like environments, and macOS if available. Watch for max-length discovery failures, residual files in the temp directory, and expected `ENAMETOOLONG` behavior for max+1 names.
