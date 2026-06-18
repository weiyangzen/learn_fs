<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/install-jdk8-on-macos/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/install-jdk8-on-macos/action.yml

Purpose: Installs Liberica JDK 8 on macOS for RocksDBJava jobs.

Important APIs/types/functions: taps `bell-sw/liberica` and installs `liberica-jdk8` via Homebrew cask.

Control flow: two bash commands run before Java build/test steps set or use `JAVA_HOME`.

State and persistence behavior: installs a JDK into the ephemeral macOS runner; no repo state is written.

Dependencies and integration points: used by macOS Java and static Java workflows. Integrates with `make jtest`, `rocksdbjavastaticosx`, and JNI CMake/make targets.

Risks: cask names, tap availability, or Apple security policy changes can break installs. Jobs set `JAVA_HOME` to a fixed Liberica path, so package layout drift matters.

Test signals: `which java`, `java -version`, `javac -version`, and Java target success validate the action.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/install-jdk8-on-macos/action.yml -->
