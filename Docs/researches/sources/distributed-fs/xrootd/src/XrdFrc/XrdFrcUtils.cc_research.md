<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcUtils.cc -->
# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcUtils.cc

## Purpose
`XrdFrcUtils.cc` implements shared FRC/FRM utility functions for administrator prompts, URL parsing, admin and queue path construction, request option mapping, single-instance locking, copy-time xattr updates, and timestamp changes.

## Important Functions
`Ask()` prompts on stderr/stdin and accepts prefix matches for yes/no/abort. `chkURL()` validates `scheme://host//path`-style URLs and returns the offset of the logical file path after compressing leading slashes. `makePath()` builds an instance-specific admin path through `XrdOucUtils::genPath()` and optionally creates it. `makeQDir()` derives the queue directory, resolves a `Queues/` symlink if present, optionally creates the directory, and returns a duplicated path. `MapM2O()` translates notification and processing option strings into `XrdFrcRequest::Options`. `MapR2Q()` maps operation characters to stage/migrate/get/put/nil queues and sets purge flags for `^` and `=` operations. `MapV2I()` maps user-visible queue listing variable names to `XrdFrcRequest::Item`. `Unique()` creates and write-locks a lock file with `fcntl()`. `updtCpy()` stores copy time in the `XrdFrm.Cpy` xattr. `Utime()` wraps `utime()` with EINTR retry.

## Control Flow, State, And Persistence
Most helpers are stateless, but `Unique()` intentionally leaks the successful lock file descriptor so the process retains the advisory lock until exit. `makePath()` and `makeQDir()` persist directories. `updtCpy()` persists extended attributes based on file `st_mtime + Adj`; FRM uses negative adjustment for migratable marking and zero/positive behavior for purgeable or lock-file compatibility. `Ask()` can stop workflows by returning `a`.

## Dependencies And Integration Points
The implementation depends on `XrdFrcRequest`, `XrdFrcTrace`, `XrdFrcXAttr`, `XrdOucUtils`, `XrdOucSxeq`, `XrdOucXAttr`, and POSIX filesystem APIs. Admin commands use `Ask()`, `updtCpy()`, and `Utime()` heavily. Configuration uses `makePath()`, proxy setup uses `makeQDir()`, and queue query code uses `MapV2I()`.

## Risks And Test Signals
Path helpers use fixed local buffers and `strcpy()`, so long admin paths and symlink targets are important tests. `MapR2Q()` uses `*Flags = Purge` for `^` but `*Flags |= Purge` for `=`, so callers must initialize flags and know the replacement behavior. `Ask()` accepts ambiguous prefixes by `strncmp()` with input length, so one-letter answers work but accidental prefixes also match. Tests should cover URL offset parsing, symlinked queue paths, lock contention, xattr byte order through `updtCpy()`, and option mapping for every operation character.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcUtils.cc -->
