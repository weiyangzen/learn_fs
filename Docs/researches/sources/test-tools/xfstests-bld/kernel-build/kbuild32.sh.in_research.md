# sources/test-tools/xfstests-bld/kernel-build/kbuild32.sh.in

Purpose: install-time wrapper for 32-bit kernel builds. It is the same as `kbuild.sh.in` but appends `--32` before user arguments.

Important control flow: substitutes `@DIR@`, exports `KBUILD_DIR`, and `exec`s `$KBUILD_DIR/kbuild --32 "$@"`.

State/persistence: none directly.

Dependencies/integration: intended to provide a stable 32-bit build command, but the current `kbuild` parser recognizes `-32` and `--i386`, not `--32`.

Risks: likely option mismatch: this wrapper passes `--32`, while `kbuild` handles `--i386|-32)`. Unless another compatibility layer rewrites it, installed `kbuild32` will hit `unknown option: --32`.

Test signals: an installed-wrapper smoke test should invoke `kbuild32 --get-build-dir`; failure would confirm the option mismatch.
