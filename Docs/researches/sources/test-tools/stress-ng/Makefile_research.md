# sources/test-tools/stress-ng/Makefile

Purpose: central stress-ng build, generation, packaging, installation, and test harness.

Important APIs and control flow: detects compiler family, kernel, architecture machine, and supported flags; applies optimization, hardening, sanitizer, LTO, static, small-build, pedantic, and verbose controls; enumerates headers, generated headers, core sources, generated core sources, and hundreds of stressor sources; generates `config.h`, `core-config.c`, `personality.h`, `io-uring.h`, `git-commit-id.h`, AppArmor data, and perf-event headers; compiles objects, links with C or C++ depending on Eigen support, and provides clean/test/dist/install/uninstall targets.

State and persistence: creates build artifacts (`*.o`, `stress-ng`, generated headers, config files, tarball, man gzip, PDF), installs under `DESTDIR`, and removes them through clean targets.

Dependencies and integration: relies on `Makefile.config`, `Makefile.machine`, compiler probes, optional libraries discovered in `config.h`, shell tools (`grep`, `sed`, `awk`, `od`, `gzip`, `tar`), AppArmor parser, git, and Debian test scripts.

Risks and test signals: large explicit source lists are easy to desynchronize; compiler probing via shell can be slow and environment-sensitive; generated headers introduce ordering dependencies; shell interpolation in flags requires trusted build inputs. Signals are `make`, `make config.h`, generated header freshness, quick/lite/slow/verify tests, and CI artifacts.
