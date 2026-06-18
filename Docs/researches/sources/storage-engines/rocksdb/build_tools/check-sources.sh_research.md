# sources/storage-engines/rocksdb/build_tools/check-sources.sh research

Purpose: `check-sources.sh` is a repository hygiene guard for RocksDB source files. It blocks common mistakes before commit or push, including hardcoded namespace names, `nocommit` markers, incorrect include styles, broad `using namespace`, and non-ASCII source bytes.

Important APIs: the script takes no explicit arguments and reports violations through stdout plus its exit status. It uses the current Git repository as its input.

Control flow: it initializes `BAD`, runs a sequence of `git grep` checks, and treats any grep result other than "no matches" as a violation. It excludes itself and selected third-party/docs paths for some checks. At the end it exits 1 if any check set `BAD`.

State and persistence: it does not mutate files. It reads tracked Git content and relies on Git pathspec filtering. Output is diagnostic text.

Dependencies and integration: dependencies are `bash`, `git grep`, `grep` semantics, and locale control for the non-ASCII scan. It integrates naturally with CI and developer pre-submit checks.

Risks and test signals: checks are intentionally simple and can produce both false positives and false negatives. `git grep` only searches Git-visible content. The `*.[ch]*` pattern is broad and may include unexpected file extensions. Tests should run in a fixture Git repo with known violations and verify that each check toggles the exit status.
