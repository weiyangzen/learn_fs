# sources/security-integrity/selinux/scripts/env_use_destdir
# sources/security-integrity/selinux/scripts/env_use_destdir

Purpose: configures environment variables so commands use libraries, binaries, Python modules, and Ruby modules installed into `DESTDIR`.

Important APIs and control flow: requires `DESTDIR`, builds `LD_LIBRARY_PATH` from DESTDIR and optional `PREFIX`, `LIBDIR`, `SHLIBDIR`, prepends DESTDIR bin/sbin paths, computes Python `platlib`/`purelib` paths with `sysconfig`, computes Ruby vendor paths with `RbConfig`, and `exec`s arguments if provided.

State and persistence: mutates current shell environment when sourced or child environment when executed; no files written.

Dependencies and integration points: used by build/test workflows after staged install.

Risks and test signals: the `PREFIX` PATH assignment appears to append `$LD_LIBRARY_PATH` instead of existing `$PATH`, which may be a bug. Shellcheck disables are present for intentional dynamic command use. No direct tests.
