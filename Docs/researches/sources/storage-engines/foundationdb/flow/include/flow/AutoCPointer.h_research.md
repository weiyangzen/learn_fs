# sources/storage-engines/foundationdb/flow/include/flow/AutoCPointer.h

Purpose: RAII wrapper for C pointers that must be released by a matching C free function.

Important APIs/types/functions: template `AutoCPointer<T, R>` deriving protected from `std::unique_ptr<T, R (*)(T*)>`, constructor overloads, `operator bool`, `release`, `reset`, and implicit `operator T*`.

Control flow: construction stores pointer and deleter; destruction invokes the deleter through `unique_ptr`; `release` transfers ownership without freeing.

State/persistence: owns one C pointer in process memory.

Dependencies/integration: intended for OpenSSL and similar C APIs where functions accept raw `T*`. Implicit conversion reduces `.get()` noise.

Risks: implicit raw pointer conversion can hide ownership/lifetime mistakes. Deleter type must match exactly and tolerate null where applicable.

Test signals: compile-time use with C APIs and leak/error-path testing around reset/release.
