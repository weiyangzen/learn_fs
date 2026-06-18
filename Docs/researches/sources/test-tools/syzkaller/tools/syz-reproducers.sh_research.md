# sources/test-tools/syzkaller/tools/syz-reproducers.sh

## Purpose
This Bash helper downloads exported C reproducers from syzkaller storage, extracts them, compiles them in parallel, and reports how many built successfully.

## Important APIs, types, and functions
- The script accepts one required target directory argument.
- It uses `wget`, `tar`, `find`, `xargs`, `grep`, `gcc`, and `wc`.
- The compile pipeline checks each `.c` file for `__NR_mmap2` and adds `-m32` when present, then builds statically with pthreads into `<target>/bin/<filename>`.

## Control flow
The script validates the target directory argument, creates it, downloads `upstream.tar.gz`, extracts and removes the archive, creates `bin`, compiles all `export/bugs/**/*.c` files with `xargs -P 128`, counts successful compilations by echoing `1`, counts total reproducers, and prints both totals.

## State and persistence behavior
Creates or reuses the target directory, downloads a remote archive, extracts an `export` tree, creates `bin`, and writes compiled binaries. It removes only the downloaded archive, not extracted sources or binaries.

## Dependencies and integration points
Depends on syz-db-export artifact layout and public Google Cloud Storage. Integrates with local C toolchains and can be used to prepare a corpus of standalone reproducer binaries.

## Risks and edge cases
No `set -euo pipefail`, so partial failures can continue. Parallelism is hard-coded to 128 and may overwhelm hosts. `grep "__NR_mmap2"` may print matched lines into build logs unless quiet mode is used. Static `-m32` builds require 32-bit libraries/toolchain support. File basenames may collide across directories.

## Test signals
No tests. Manual validation should cover download failure, extraction failure, no `.c` files, compile failures, 32-bit reproducers, and duplicate basenames.
