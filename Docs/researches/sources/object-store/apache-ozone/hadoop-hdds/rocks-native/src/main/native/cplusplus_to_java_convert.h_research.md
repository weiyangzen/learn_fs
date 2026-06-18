<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/native/cplusplus_to_java_convert.h -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/native/cplusplus_to_java_convert.h

## Purpose

Provides the `GET_CPLUSPLUS_POINTER` macro used by JNI code to safely convert C++ pointers to Java `jlong` handles on both 32-bit and 64-bit platforms.

## Important APIs, types, and functions

The single API is `GET_CPLUSPLUS_POINTER(_pointer)`, implemented as `static_cast<jlong>(reinterpret_cast<size_t>(_pointer))`.

## Control flow

There is no runtime control flow; JNI C++ code includes the header and uses the macro when returning native pointer handles to Java.

## State and persistence behavior

No state is stored. Java objects persist returned handles as long fields and pass them back to native methods.

## Dependencies and integration points

Included by ManagedRawSSTFileReader.cpp and ManagedRawSSTFileIterator.cpp. It depends on JNI code treating the reverse cast from jlong to pointer consistently.

## Risks and edge cases

Incorrect pointer conversion can make handles negative on 32-bit systems or truncate pointers. The macro addresses the return path, but callers must still avoid using handles after native deletion.

## Test signals

Native tests on 32-bit-compatible and 64-bit platforms, plus handle lifecycle tests that create and close readers/iterators repeatedly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/native/cplusplus_to_java_convert.h -->
