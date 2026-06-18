# sources/user-network-fs/s3fs-fuse/test/compile_all_targets.sh

## Purpose
Build matrix script that compiles s3fs-fuse under several TLS/crypto backends, language modes, word sizes, and compilers.

## Important APIs, Types, And Control Flow
The script enables `errexit`, `nounset`, and `pipefail`, sets `COMMON_FLAGS='-O -Wall -Werror'`, then repeatedly runs `make clean`, `./configure` with a variant, and parallel `make`. Variants cover GnuTLS, GnuTLS+Nettle, NSS, OpenSSL, C++23, `-m32`, and clang++ with `-Wshorten-64-to-32`.

## State And Persistence
Mutates the working tree build directory through configure outputs, object files, and clean/build cycles. No source files are edited.

## Dependencies And Integration Points
Depends on autotools/configure, make, nproc, backend development libraries, clang++, and 32-bit toolchain support. It complements runtime tests by checking optional compile targets.

## Risks And Test Signals
`-Werror` makes warning churn fail the matrix. `-m32` is environment-sensitive. The script is serial across configurations and can be expensive. A complete zero exit is strong build portability signal.
