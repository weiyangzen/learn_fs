# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/EnvironmentTest.java

Purpose: JUnit tests for RocksJava `Environment` platform detection and JNI/shared-library filename construction.

Important APIs/types/functions: `Environment.isWindows`, `isUnix`, `isPowerPC`, `isAarch64`, `is64Bit`, `getJniLibraryExtension`, `getJniLibraryFileName`, `getFallbackJniLibraryFileName`, `getSharedLibraryFileName`, `getSharedLibraryName`, `getJniLibraryName`, `initIsMuslLibc`, reflection helpers for static fields.

Control flow and state: `saveState` records initial static `Environment` fields. Each test uses reflection to inject OS/arch/musl combinations, then asserts expected platform predicates and library names for macOS, Linux glibc/musl, Unix, AIX, Windows, ppc64le, and aarch64. `restoreState` restores all fields after the class.

State and persistence behavior: mutates global static process state in `Environment`; no file persistence. The restore method is essential to avoid leaking fake OS state into other tests.

Dependencies and integration points: tests the naming contract consumed by `NativeLibraryLoader` and packaging of RocksJava native artifacts.

Risks: reflection against private static fields is brittle and unsafe under parallel execution. JDK module/access changes can break reflective field writes. Musl detection is partially simulated and does not probe real libc here.

Test signals: good table-like coverage of supported platform filename mappings and unsupported AIX 32-bit behavior.
