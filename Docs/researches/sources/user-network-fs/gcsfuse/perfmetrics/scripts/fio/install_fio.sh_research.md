## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/install_fio.sh

Purpose: Installs a patched source build of fio for performance tests.

APIs and control flow: Requires one argument, the directory under which to clone fio. Installs `libaio-dev`, removes an existing `$SRC_DIR/fio`, clones `https://github.com/axboe/fio.git`, checks out `fio-3.36`, patches `FIO_IO_U_PLAT_GROUP_NR` in `stat.h` to `32`, configures, builds, installs, prints `fio -version`, and returns to the original directory.

State and persistence: Mutates the source directory, installs system packages, and installs fio globally via `sudo make install`.

Dependencies and risks: Requires sudo, apt, git, build tooling, network access, and an unchanged `stat.h` pattern. `cd -` prints the previous directory and can fail if shell state is unusual.

Test signals: Printed `fio version=` is the verification point; no unit tests.
