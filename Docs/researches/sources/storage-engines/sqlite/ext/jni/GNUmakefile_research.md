# sources/storage-engines/sqlite/ext/jni/GNUmakefile

## Purpose
`ext/jni/GNUmakefile` bootstraps SQLite JNI bindings on Linux-like systems. It compiles Java sources, generates JNI headers, builds `libsqlite3-jni.so`, runs tests, builds a jar, generates javadocs, and creates distribution zips.

## Important Variables, Targets, And Rules
Key variables include `JAVA_HOME`, `JDK_HOME`, `dir.*` source/build paths, `enable.fts5`, `enable.tester`, `opt.threadsafe`, `opt.fatal-oom`, `opt.debug`, `opt.metrics`, `opt.extras`, `SQLITE_OPT`, `JAVA_FILES.*`, `CLASS_FILES.*`, `sqlite3-jni.h`, and `package.dll`. Important targets include `all`, class rules, `$(sqlite3.h)`, `$(sqlite3-jni.h)`, `$(package.dll)`, `test`, `tester`, `multitest`, `jar`, `doc`, `clean`, `distclean`, `dist`, and `snapshot`.

## Control Flow
The default target builds classes and the shared library. Java files are enumerated explicitly. `javac -h` emits JNI headers into `bld`; selected headers are concatenated into checked-in `src/c/sqlite3-jni.h` if content changed. The shared library compiles `sqlite3-jni.c` with JDK/SQLite include paths and `SQLITE_OPT`. Test targets run Java classes with `java.library.path` pointing at the build directory. Jar and dist targets package generated artifacts and canonical SQLite sources.

## State And Persistence
The makefile writes `bld` outputs, `.class` files beside Java sources, generated JNI headers, a jar, javadocs, and dist zips. It may update checked-in `sqlite3-jni.h`.

## Dependencies And Integration Points
It depends on a JDK, C compiler, SQLite canonical `sqlite3.c/h`, JNI C/Java sources, optional tests, top-level SQLite make targets, and `version-info`.

## Risks
It assumes Linux-like shared-library conventions. Class files are emitted into the source tree. Regenerating `sqlite3-jni.h` with `enable.fts5=0` can strip FTS5 APIs. Some generated-header dependencies are serialized with `.NOTPARALLEL`, but not the entire build graph.

## Test Signals
Run `make all`, `make test`, `make tester` when scripts exist, `make multitest`, `make jar`, `run-jar`, and cleanup targets. Verify both FTS5-enabled and disabled builds deliberately.
