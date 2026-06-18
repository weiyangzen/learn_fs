# sources/test-tools/ltp/testcases/kernel/fs/fs_maim/backbeat

Purpose: Perl helper that simulates an online backup across three mounted partitions by copying `/sbin`, archiving it, moving the archive, extracting it elsewhere, and diffing the result.

Important APIs/types/functions: Perl backticks for `cp -aL`, `tar`, `mv`, `diff`, `mkdir`, `chdir`, argument parsing by splitting `/dev/name` paths, and exit status 0/1.

Control flow: derives directory names from three device path arguments, creates `<part1>/sbin`, copies `/sbin` into it, tars from partition 1, moves the tarball to partition 2, extracts to partition 3, then compares partition 3's `sbin` tree to partition 1's original copy.

State/persistence behavior: writes directories, a tar archive, and extracted files inside the current working directory's partition-named mount points.

Dependencies/integration: called by `maimparts` after `partbeat` formats and mounts three partitions. Depends on Perl, `/sbin`, `cp`, `tar`, `mv`, and `diff`.

Risks/test signals: argument parsing assumes `/dev/name` paths with exactly three slash-separated fields. It follows symlinks with `cp -aL`, so backup content depends on host `/sbin`. Success is `Diff: PASS` and exit 0; any diff output produces exit 1.
