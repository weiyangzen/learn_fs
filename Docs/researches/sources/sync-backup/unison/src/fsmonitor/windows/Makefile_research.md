# sources/sync-backup/unison/src/fsmonitor/windows/Makefile

Purpose: Windows fsmonitor build fragment.

Important variables: `FSMOCAMLOBJS` includes marshalling, regex/unicode support, Windows system modules, Lwt Windows modules, watcher common code, and Windows watcher; `FSMCOBJS` includes bytearray, Windows system, Lwt, xattr, ACL, and copy stubs; dependencies ensure watcher objects wait for `lwt/win/lwt_win`.

Control flow: no executable rules beyond dependency declarations consumed by the parent build.

State/persistence: determines object linkage for Windows `unison-fsmonitor`.

Dependencies/integration: ties together Windows system wrappers, async Lwt stubs, property stubs, and watcher code.

Risks: Windows fsmonitor depends on many native stubs; missing one can link but fail at runtime if optional external declarations drift. Object extensions use `$(OBJ_EXT)` for compiler portability.

Test signals: Windows CI `make fsmonitor`, local `unison-fsmonitor.exe` startup, and watcher integration tests.
