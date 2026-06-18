# Research: sources/storage-engines/rocksdb/third-party/gtest-1.8.1/fused-src/gtest/gtest.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008688`: lines 1-6519, `Docs/researches/chunks/subset-b-008688_research.md`
- `subset-b-008689`: lines 6520-12679, `Docs/researches/chunks/subset-b-008689_research.md`
- `subset-b-008690`: lines 12680-18782, `Docs/researches/chunks/subset-b-008690_research.md`
- `subset-b-008691`: lines 18783-22095, `Docs/researches/chunks/subset-b-008691_research.md`

## Chunk Research

### subset-b-008688: lines 1-6519

# sources/storage-engines/rocksdb/third-party/gtest-1.8.1/fused-src/gtest/gtest.h lines 1-6519

## Scope And Purpose

This chunk is the opening portion of RocksDB's vendored, fused Google Test 1.8.1 public header. It begins with the public `gtest/gtest.h` include guard, but because this is a fused distribution it immediately inlines several normally separate Google Test internal headers: `gtest/internal/gtest-port.h`, `gtest/internal/gtest-port-arch.h`, `gtest/internal/custom/gtest-port.h`, the optional generated tuple fallback, `gtest-message.h`, `gtest-string.h`, `gtest-filepath.h`, and the beginning of the generated `gtest-type-util.h`.

The chunk's main job is to make the rest of Google Test portable and self-contained. It detects operating systems, compilers, C++ language/library capabilities, regular-expression support, RTTI, exceptions, pthreads, death-test support, typed-test support, tuple implementations, stream redirection, DLL visibility, sanitizer attributes, and filesystem path conventions. It also declares the internal utility types that later public assertions, death tests, typed tests, XML output, and test registration code build on.

This is mostly infrastructure and declarations rather than executable test logic. The code exists so RocksDB's C++ tests can include a single vendored header without relying on a system Google Test installation. The chunk ends mid-way through the generated type-template list machinery, at the start of the `Templates24` declaration; later chunks continue the generated type utilities and the public Google Test API.

## Fused Header Layout

The file preserves the original Google Test header boundaries with their own include guards. Important boundaries in this chunk are:

- `GTEST_INCLUDE_GTEST_GTEST_H_`: outer public header guard.
- `GTEST_INCLUDE_GTEST_INTERNAL_GTEST_INTERNAL_H_`: internal declarations later used by the public API.
- `GTEST_INCLUDE_GTEST_INTERNAL_GTEST_PORT_H_`: the core portability layer.
- `GTEST_INCLUDE_GTEST_INTERNAL_GTEST_PORT_ARCH_H_`: platform macro detection.
- `GTEST_INCLUDE_GTEST_INTERNAL_CUSTOM_GTEST_PORT_H_`: empty customization injection point in this fused copy.
- `GTEST_INCLUDE_GTEST_INTERNAL_GTEST_TUPLE_H_`: generated in-header TR1 tuple fallback when the platform cannot provide one.
- `GTEST_INCLUDE_GTEST_GTEST_MESSAGE_H_`: declaration of the stream-accumulating `testing::Message`.
- `GTEST_INCLUDE_GTEST_INTERNAL_GTEST_STRING_H_`: internal string utilities.
- `GTEST_INCLUDE_GTEST_INTERNAL_GTEST_FILEPATH_H_`: internal filesystem path helper.
- `GTEST_INCLUDE_GTEST_INTERNAL_GTEST_TYPE_UTIL_H_`: generated typed-test support, started here and continued after this chunk.

Because the header is fused, comments saying "include this header" or "do not include separately" refer to the original upstream layout, not separate files in this vendored tree.

## Platform And Feature Detection

The portability layer defines `GTEST_OS_*` macros from compiler/platform predefined macros. Covered targets include Cygwin, Symbian, Windows desktop/mobile/phone/RT/MinGW, macOS/iOS, FreeBSD, Fuchsia, Linux/Android, z/OS, Solaris, AIX, HP-UX, Native Client, NetBSD, OpenBSD, and QNX. These macros drive most later conditional code.

Compiler and standard-library capability detection includes:

- `GTEST_GCC_VER_` for GCC-style version checks.
- `GTEST_LANG_CXX11` and `GTEST_STDLIB_CXX11` to distinguish language mode from standard-library feature availability.
- `GTEST_HAS_STD_BEGIN_AND_END_`, `GTEST_HAS_STD_FORWARD_LIST_`, `GTEST_HAS_STD_FUNCTION_`, `GTEST_HAS_STD_INITIALIZER_LIST_`, `GTEST_HAS_STD_MOVE_`, `GTEST_HAS_STD_UNIQUE_PTR_`, `GTEST_HAS_STD_SHARED_PTR_`, `GTEST_HAS_UNORDERED_MAP_`, and `GTEST_HAS_UNORDERED_SET_`.
- `GTEST_HAS_STD_TUPLE_`, `GTEST_HAS_TR1_TUPLE`, and `GTEST_USE_OWN_TR1_TUPLE`, which decide whether `std::tuple`, `std::tr1::tuple`, or Google Test's generated tuple fallback is used.
- `GTEST_HAS_EXCEPTIONS`, `GTEST_HAS_RTTI`, `GTEST_HAS_PTHREAD`, `GTEST_HAS_POSIX_RE`, `GTEST_USES_POSIX_RE`, `GTEST_USES_SIMPLE_RE`, `GTEST_HAS_CLONE`, `GTEST_HAS_STREAM_REDIRECTION`, `GTEST_HAS_DEATH_TEST`, `GTEST_HAS_TYPED_TEST`, `GTEST_HAS_TYPED_TEST_P`, and `GTEST_HAS_COMBINE`.
- `GTEST_HAS_CXXABI_H_` for demangling type names on libstdc++/libc++ platforms.
- `GTEST_HAS_SEH` and `GTEST_IS_THREADSAFE` for Windows structured exception handling and synchronization availability.

The detection code intentionally makes every user-tweakable capability macro resolve to `1` or `0` after inclusion. Users and build scripts can override the user-facing `GTEST_HAS_*` knobs before including the header, but the `GTEST_OS_*` platform macros are meant to be owned by Google Test.

## Export, Attribute, And Utility Macros

This chunk defines many internal macros used throughout the rest of the fused header and implementation:

- `GTEST_API_` controls DLL import/export on MSVC and default symbol visibility on GCC/Clang.
- `GTEST_DISABLE_MSC_WARNINGS_PUSH_`, `GTEST_DISABLE_MSC_WARNINGS_POP_`, `GTEST_DISABLE_MSC_DEPRECATED_PUSH_`, and `GTEST_DISABLE_MSC_DEPRECATED_POP_` wrap compiler warning suppression.
- `GTEST_ATTRIBUTE_UNUSED_`, `GTEST_ATTRIBUTE_PRINTF_`, `GTEST_MUST_USE_RESULT_`, `GTEST_NO_INLINE_`, and sanitizer suppression attributes annotate declarations portably.
- `GTEST_DISALLOW_ASSIGN_` and `GTEST_DISALLOW_COPY_AND_ASSIGN_` disable copying in pre-C++11 style, using `= delete` when available.
- `GTEST_AMBIGUOUS_ELSE_BLOCKER_` supports assertion macros in nested `if` statements.
- `GTEST_CHECK_` and `GTEST_CHECK_POSIX_SUCCESS_` provide internal fatal checks used by synchronization and runtime helpers.
- `GTEST_FLAG`, `GTEST_DECLARE_bool_`, `GTEST_DECLARE_int32_`, `GTEST_DECLARE_string_`, `GTEST_DEFINE_bool_`, `GTEST_DEFINE_int32_`, and `GTEST_DEFINE_string_` declare and define Google Test flags.
- `GTEST_SNPRINTF_`, `GTEST_PATH_SEP_`, and `GTEST_HAS_ALT_PATH_SEP_` abstract standard-library and filesystem differences.

These macros are the compile-time control plane for the rest of Google Test. Changes here have broad impact because public assertion macros, typed-test macros, death tests, XML output, and flag parsing depend on them.

## Tuple And Type-List Support

If the platform has usable `std::tuple`, the chunk imports tuple symbols from `std`. If TR1 tuple is available but `std::tuple` is not, it imports from `std::tr1`. If neither path is reliable, Google Test's generated fallback implementation is compiled under `namespace std { namespace tr1 { ... } }`.

The fallback tuple implementation supports arities 0 through 10. It defines:

- `tuple<>` and `tuple<T0, ..., T9>` storage classes with fields `f0_` through `f9_`.
- `make_tuple()` overloads for arities 0 through 10.
- `tuple_size` and `tuple_element`.
- `get<k>()` through `gtest_internal::Get<k>`.
- Equality and inequality through recursive `SameSizeTuplePrefixComparator`.
- Helper traits such as `ByRef`, `AddRef`, and `TupleElement`.

The tuple implementation is intentionally limited to what Google Test needs for parameterized and typed tests. It only implements `==` and `!=`, not the full TR1 relational-operator set. It also has compiler-specific escapes for Symbian, old Sun Studio, old GCC without RTTI, MSVC TR1 behavior, and Boost TR1 interactions on Symbian.

The generated `gtest-type-util.h` section begins at line 4613. In this chunk it defines:

- `CanonicalizeForStdLibVersioning()`, which normalizes names like `std::__1::vector` to reduce type-name noise across standard-library versions.
- `GetTypeName<T>()`, which uses RTTI plus `abi::__cxa_demangle` or HP aCC demangling when available, otherwise returns the raw `typeid` name or `"<type>"` when RTTI is disabled.
- `AssertTypeEq<T1, T2>` for compile-time type equality.
- `None`, `Types0`, and generated `Types1` through `Types50`, each represented as a cons-style list with `Head` and `Tail`.
- The public `Types<T1, ..., T50>` facade and partial specializations that translate trailing `None` defaults to the shorter internal `TypesN`.
- The start of template-list support: `TemplateSel`, `GTEST_BIND_`, `NoneT`, `Templates0`, and `Templates1` through the beginning of `Templates24`.

The generated sections are large and repetitive by design. They simulate variadic templates and template-template parameter lists for C++03-era compilers while keeping typed-test compiler diagnostics more readable.

## Important APIs, Types, And Functions

Key internal APIs and declarations introduced in this chunk include:

- `testing::Message`: a small stream accumulator used for assertion failure messages. It stores a `std::stringstream`, handles null pointers consistently, streams bools as `true`/`false`, supports narrow stream manipulators, and declares UTF-8 conversions for wide strings.
- `testing::internal::StreamableToString()`: converts a streamable value to a string via `Message`, preserving Google Test's null-pointer and embedded-NUL conventions.
- `testing::internal::RE`: a regular-expression wrapper over POSIX regex, PCRE when injected, or Google Test's simple regex engine. It exposes `FullMatch()` and `PartialMatch()` overloads for C strings and standard/global strings.
- `testing::internal::String`: static string utilities for C-string cloning, null-safe comparisons, wide-string display, case-insensitive comparisons, suffix checks, and numeric formatting.
- `testing::internal::StringStreamToString()`: extracts stream text while escaping embedded NUL characters.
- `testing::internal::FilePath`: a normalized path value object used by XML output and output-file naming. It handles current directory discovery, filename construction, path concatenation, unique-name generation, path component removal, extension stripping, recursive directory creation, existence checks, root checks, absolute-path checks, and platform path separators.
- `testing::internal::GTestLog`: RAII logging object used by `GTEST_LOG_`; fatal severity aborts in its destructor.
- `testing::internal::Mutex`, `MutexBase`, `MutexLock`, `Notification`, `ThreadWithParam`, `ThreadLocal`, and related thread-local value-holder classes: platform-specific synchronization and helper-thread primitives for death tests and Google Test's own internal concurrency.
- `testing::internal::AutoHandle`: Windows handle ownership wrapper used when Windows threading/death-test support is active.
- `testing::internal::TypeWithSize`, `Int32`, `UInt32`, `Int64`, `UInt64`, `TimeInMillis`, `BiggestInt`, and `kMaxBiggestInt`: fixed-size integer abstractions used by flags and later floating-point comparison code.
- `testing::internal::ImplicitCast_`, `DownCast_`, and `CheckedDowncastToActualType`: controlled cast helpers, with RTTI-backed validation when available.
- `testing::internal::bool_constant`, `true_type`, `false_type`, `is_same`, `is_pointer`, and `IteratorTraits`: small type traits used by message streaming, typed tests, and template utilities.
- `testing::internal::posix`: wrappers for `stat`, `isatty`, string comparison/duplication, directory removal, file descriptor operations, `fopen`, `freopen`, `fdopen`, `read`, `write`, `close`, `strerror`, `getenv`, and `abort`, with Windows and mobile variants hidden behind one namespace.
- Flag/environment declarations: `ParseInt32`, `BoolFromGTestEnv`, `Int32FromGTestEnv`, `OutputFlagAlsoCheckEnvVar`, and `StringFromGTestEnv`.
- Stream-capture declarations: `CaptureStdout`, `GetCapturedStdout`, `CaptureStderr`, and `GetCapturedStderr` when stream redirection is available.
- Death-test argv declarations: `GetInjectableArgvs`, `SetInjectableArgvs`, and `ClearInjectableArgvs` when death tests are available.

RocksDB has a local modification in this chunk: `testing::internal::scoped_ptr<T>` is changed to an alias of `std::unique_ptr<T>` to avoid clang-analyzer false reports, with the original partial `scoped_ptr` implementation left commented out. This means this vendored header assumes `std::unique_ptr` is available in RocksDB's build mode even though upstream Google Test 1.8.1 still carried C++03-era fallback code.

## Control Flow

Most control flow in this chunk is preprocessor-driven. Inclusion starts by setting platform and feature macros, then conditionally includes system headers, selects tuple support, selects regex support, and chooses synchronization implementations.

Runtime control flow is concentrated in small RAII and wrapper classes:

- `GTestLog` formats a log prefix on construction and flushes or aborts on destruction for fatal checks.
- `GTEST_CHECK_` evaluates a condition through `IsTrue`; on failure it constructs a fatal `GTestLog` stream and aborts at the end of the temporary object's lifetime.
- `RE` stores compiled regex state or simple-regex patterns and routes `FullMatch`/`PartialMatch` through implementation selected at compile time.
- `Message::operator<<` routes pointer types to a null-safe overload and non-pointer values through normal stream insertion plus argument-dependent lookup.
- `Notification` on pthread platforms spins with a mutex-protected `notified_` flag and short sleeps until `Notify()` is called. Windows uses an event handle through `AutoHandle`.
- `ThreadWithParam` constructs a native thread only after member initialization, waits on an optional `Notification`, calls the user-supplied function, and joins in `Join()` or the destructor.
- `MutexLock` locks in its constructor and unlocks in its destructor.
- `ThreadLocal<T>` lazily creates per-thread `ValueHolder<T>` instances. On pthreads it uses `pthread_key_create`, `pthread_getspecific`, and `pthread_setspecific`; on Windows it delegates to `ThreadLocalRegistry`; without thread support it collapses to a single stored value.
- `FilePath` constructors normalize paths immediately, while path-manipulation methods return new `FilePath` values or filesystem status booleans.
- `GetTypeName<T>()` branches on RTTI and demangling support to produce the best available human-readable type name.

Several declarations in this chunk are implemented later in the fused source, not here. This includes most non-inline methods for `RE`, `Message`, `String`, `FilePath`, Windows synchronization, stream capture, flag parsing, and environment parsing.

## State And Persistence Behavior

There is no application-level persistence in this chunk. The state is internal test-framework state, mostly scoped to a process and often scoped to an object lifetime:

- Preprocessor macros persist for the translation unit after inclusion and determine all later Google Test API availability.
- `Message` owns a heap-allocated `std::stringstream` through RocksDB's `scoped_ptr` alias and snapshots another `Message` by copying its rendered string.
- `RE` owns the copied pattern text plus compiled POSIX regex objects or simple-regex pattern state, depending on the selected backend.
- `GTestLog` stores only severity for its destructor behavior.
- `MutexBase` stores `pthread_mutex_t`, owner tracking, and `has_owner_`; static mutexes are link-time initialized.
- Windows `Mutex` stores owner thread ID, initialization phase, and a lazily initialized critical-section pointer.
- `Notification` stores a pthread mutex plus boolean flag on pthread platforms or an event handle on Windows.
- `ThreadLocal<T>` stores either a `pthread_key_t`, a Windows registry association, or a single fallback value. The comments explicitly warn that thread-local values on other threads may not be destroyed if the `ThreadLocal` object is destroyed while those threads are still alive.
- `FilePath` stores only its normalized `pathname_` string. Its methods may inspect or create filesystem directories but do not cache filesystem state.
- Death-test injectable argv declarations imply process-global argument state in later implementation code.
- Google Test flags declared through macros are process-global variables named with the `FLAGS_gtest_` prefix.

The only filesystem mutations declared in this chunk are `FilePath::CreateDirectoriesRecursively()` and `FilePath::CreateFolder()`, whose implementations are later. `GenerateUniqueFileName()` is explicitly documented as race-prone if multiple processes call it concurrently.

## Dependencies And Integration Points

This chunk integrates with several layers:

- C and C++ standard library headers: `stddef.h`, `stdlib.h`, `stdio.h`, `string.h`, `ctype.h`, `float.h`, `limits`, `memory`, `ostream`, `iostream`, `sstream`, `string`, `vector`, `algorithm`, `utility`, `map`, and `set`.
- POSIX APIs on Unix-like platforms: `unistd.h`, `strings.h`, `sys/types.h`, `sys/stat.h`, `pthread.h`, `time.h`, `regex.h`, `read`, `write`, `close`, `stat`, `rmdir`, `chdir`, `fileno`, and `nanosleep`.
- Windows C runtime and OS abstractions: `direct.h`, `io.h`, `_stat`, `_isatty`, `_stricmp`, `_strdup`, `_fileno`, `_rmdir`, `_snprintf_s`, `CRITICAL_SECTION` forward declarations, Windows family detection, and Windows handle/event abstractions without directly including `windows.h`.
- Apple and Android platform headers: `AvailabilityMacros.h`, `TargetConditionals.h`, and `android/api-level.h`.
- ABI demangling: `cxxabi.h` or HP aCC demangling headers when available.
- Boost TR1 tuple interactions on Symbian.
- Later Google Test fused implementation sections that define the declared methods and consume these macros and types.
- RocksDB's test build as a vendored third-party dependency. RocksDB test code normally includes this through Google Test headers rather than calling these internal APIs directly.

The public integration surface exposed by this chunk is still small: `testing::Message`, `testing::tuple`/`make_tuple`/`Types` when enabled, and flag/macros that public Google Test headers later use. Most symbols live in `testing::internal` and are documented as unstable implementation details.

## Risks And Edge Cases

This chunk is high risk because it sits below every Google Test assertion and registration macro:

- Feature-detection mistakes can silently disable death tests, typed tests, tuple support, stream capture, pthreads, or regex support on a platform.
- The RocksDB `scoped_ptr` alias to `std::unique_ptr` narrows compatibility compared with upstream's original C++03-friendly `scoped_ptr`. Builds that try to compile this vendored header without a usable C++11 `std::unique_ptr` will fail.
- The fallback tuple implementation defines symbols inside `std::tr1`; the code comments acknowledge this is only acceptable because it is acting like a standard-library vendor. It is a compatibility hack, not a pattern to extend casually.
- `GTEST_CHECK_POSIX_SUCCESS_` aborts on pthread and POSIX errors, so synchronization failures are process-fatal rather than reported as normal test failures.
- `Notification::WaitForNotification()` on pthreads polls every 10 ms instead of using a condition variable. It is simple but can delay tests or spin under scheduler stress.
- Thread-local lifetime rules are subtle. Destroying a `ThreadLocal` while other threads still have values can leak or leave platform-specific cleanup gaps.
- `DownCast_` and `CheckedDowncastToActualType` rely on RTTI only when enabled; without RTTI they fall back to static casts.
- `Message` null-pointer handling avoids undefined stream behavior, but custom `operator<<` lookup depends on ADL and the global `operator<<` declaration for `Secret`.
- Wide-string case-insensitive comparisons are locale-sensitive and explicitly differ across Windows, GNU, and macOS.
- `FilePath` normalization only collapses repeated separators and maps alternate separators on Windows. It intentionally does not resolve `.` or `..`, validate illegal characters, or guarantee that paths exist.
- `FilePath::GenerateUniqueFileName()` can race across processes because existence checking and creation are separate.
- `GetTypeName<T>()` depends on RTTI, ABI demangling availability, and standard-library inline namespace normalization. Type names can still vary across toolchains.
- The generated `Types` and `Templates` sections cap type-parameter lists at 50 entries. Tests exceeding that generated limit cannot be represented by this version's typed-test machinery.
- Because this is a fused vendored header, hand edits must preserve upstream-generated boundaries, include guards, and conditional compilation balance. A small preprocessor imbalance can break all RocksDB C++ tests.

## Test Signals

The most relevant validation signals for this chunk are compile-time and Google Test self-test style checks:

- RocksDB C++ test targets including this header should compile on the supported compiler matrix, proving the platform macros, headers, `std::unique_ptr`-based `scoped_ptr`, tuple selection, and synchronization declarations are compatible.
- Tests using ordinary assertions should render `testing::Message` output correctly, including bools, null pointers, wide strings, embedded NUL escaping, and types with stream operators found by ADL.
- Regex-dependent Google Test filters and death-test expectations should pass on POSIX-regex and simple-regex platforms.
- Typed and type-parameterized tests should compile and report readable type names through `GetTypeName<T>()`, `Types<>`, and the generated type-list machinery.
- Death-test builds should validate `GTEST_HAS_DEATH_TEST`, injectable argv handling, clone/Windows process support, and stream capture declarations on platforms where those features are enabled.
- Threaded Google Test internals should pass under pthread and Windows builds, especially mutex ownership checks, `ThreadWithParam`, `Notification`, and `ThreadLocal` cleanup.
- XML-output and output-file tests should exercise `FilePath` path joining, normalization, extension removal, unique-name generation, directory creation, and platform separators.
- Flag parsing tests should exercise `ParseInt32`, `BoolFromGTestEnv`, `Int32FromGTestEnv`, `StringFromGTestEnv`, and the `GTEST_FLAG` declaration/definition macros.
- Cross-platform builds are the strongest signal because much of the chunk is conditional. Linux-only success does not cover Windows, mobile Windows exclusions, Android API-level gates, Symbian/Sun/IBM compatibility paths, or the no-pthread fallback.

### subset-b-008689: lines 6520-12679

# sources/storage-engines/rocksdb/third-party/gtest-1.8.1/fused-src/gtest/gtest.h lines 6520-12679

## Chunk Scope

This chunk is a large fused Google Test 1.8.1 header slice. It starts in the generated typed-test template list utilities and runs through internal assertion helpers, typed-test registration, death-test public/internal APIs, parameterized-test internals, universal value printers, and the beginning of generated `ValueArrayN` helpers for `Values(...)`. The slice begins mid generated `TemplatesN` series and ends mid `ValueArray15`; adjacent chunks are needed for the complete generated ranges and public macro definitions that reference these internals.

## Purpose

The code provides much of Google Test's test declaration and diagnostics machinery:

- Typed-test and type-parameterized-test infrastructure that maps user-friendly `Types<...>`/`Templates<...>` declarations into recursive type lists and registers every fixture/test/type combination.
- Assertion plumbing for boolean, exception, fatal/nonfatal, and test declaration macros.
- Death-test interfaces and macros, including parent/child role selection, child process execution, exit-status predicates, unsupported-platform fallbacks, and debug-only death assertions.
- Parameterized-test generator, iterator, factory, and registry internals used by `TEST_P` and `INSTANTIATE_TEST_CASE_P`.
- Universal printing and comparison formatting used in assertion failure messages.
- A small reference-counted `linked_ptr` implementation used to share immutable generator and test metadata.

## Important APIs, Types, and Functions

### Typed Template Utilities

- `Templates24` through `Templates50` and `Templates<...>::type` build recursive type-list-like structures for template template parameters. Each `TemplatesN` exposes `Head = TemplateSel<T1>` and `Tail = TemplatesN-1<...>`.
- The `Templates<...>` primary template defaults all 50 parameters to `NoneT` and maps full input to `Templates50`. Its generated partial specializations collapse trailing `NoneT` parameters to `Templates0` through `Templates49`, improving compiler diagnostics by avoiding huge default-argument dumps.
- `TypeList<T>` maps either a single type or a `Types<...>` pack into an internal `TypesN` list so typed-test macros can accept both forms.
- `DefaultNameGenerator`, `NameGeneratorSelector`, `GenerateNamesRecursively`, and `GenerateNames` generate type-name suffixes for typed-test instantiations. Default names are integer indexes unless a user-provided generator is selected.
- `TypedTestCasePState` tracks names and source locations of type-parameterized tests defined before `REGISTER_TYPED_TEST_CASE_P`. `AddTestName()` aborts if definitions are attempted after registration; `VerifyRegisteredTestNames()` is declared here for cross-checking macro-provided names.
- `TypeParameterizedTest<Fixture, TestSel, Types>::Register()` recursively registers one typed test for every type in `Types`.
- `TypeParameterizedTestCase<Fixture, Tests, Types>::Register()` recursively walks test templates and calls `TypeParameterizedTest` for each test/type combination.

### Assertion and Test Registration Internals

- `GTEST_CONCAT_TOKEN_`, `GTEST_STRINGIFY_`, `GTEST_MESSAGE_AT_`, `GTEST_FATAL_FAILURE_`, `GTEST_NONFATAL_FAILURE_`, and `GTEST_SUCCESS_` are low-level macro helpers for generated assertion code.
- `GoogleTestFailureException` is the exception type thrown when `throw_on_failure` is enabled and exceptions are available.
- `AppendUserMessage`, `EqFailure`, `GetBoolAssertionFailureMessage`, `DiffStrings`, and the `edit_distance` functions are declared diagnostic builders for assertion messages and unified string diffs.
- `FloatingPoint<RawType>` wraps `float`/`double` bit patterns and implements ULP-based comparison via `AlmostEquals()`. It exposes masks for sign, exponent, and fraction bits, handles NaN as never equal, and treats signed zero correctly through sign-and-magnitude to biased conversion.
- `TypeId`, `TypeIdHelper<T>`, `GetTypeId<T>()`, and `GetTestTypeId()` provide fixture identity checking by using the address of a per-template static `dummy_`.
- `TestFactoryBase` and `TestFactoryImpl<TestClass>` abstract construction of test objects for normal and parameterized registration.
- `MakeAndRegisterTestInfo()` is the central integration point that records test case name, test name, type/value parameters, source location, fixture type id, setup/teardown hooks, and a factory.
- `GTEST_TEST_` expands a user test into a generated subclass, static `TestInfo* const test_info_`, registration through `MakeAndRegisterTestInfo()`, and the `TestBody()` definition point.

### Type Traits, Containers, and Native Arrays

- `RemoveReference`, `RemoveConst`, and `GTEST_REMOVE_REFERENCE_AND_CONST_` normalize types for static checks and array wrappers.
- `ImplicitlyConvertible<From, To>` uses overload resolution and `sizeof` to compute implicit convertibility at compile time.
- `IsAProtocolMessage<T>` detects classic protobuf message pointers by implicit conversion to forward-declared `ProtocolMessage` or `proto2::Message`.
- `IsContainerTest`, `IsHashTable`, `HasValueType`, `IsRecursiveContainerImpl`, and `IsRecursiveContainer` identify STL-like containers while avoiding recursive container printing traps.
- `ArrayEq`, `ArrayAwareFind`, and `CopyArray` recursively compare/search/copy native arrays, including multidimensional arrays.
- `NativeArray<Element>` adapts native arrays to a read-only STL-like container. It can either reference the source (`RelationToSourceReference`) or deep-copy it (`RelationToSourceCopy`), and its destructor deletes only copied storage.

### Death Test APIs

- `DeathTest` is the abstract controller for `ASSERT_DEATH`, `EXPECT_DEATH`, `ASSERT_EXIT`, and `EXPECT_EXIT`. `Create()` chooses a concrete implementation based on death-test flags, `AssumeRole()` returns parent/child role, `Wait()` obtains child status, `Passed()` evaluates exit and stderr matching, and `Abort()` reports child-side failures.
- `DeathTest::ReturnSentinel` aborts a child death test if the tested statement returns normally out of a scope where it should terminate.
- `DeathTestFactory` and `DefaultDeathTestFactory` provide a factory seam for concrete death-test creation.
- `InternalRunDeathTestFlag` owns parsed `--gtest_internal_run_death_test` fields and closes `write_fd_` in its destructor.
- `GTEST_DEATH_TEST_` is the core macro: it creates a `DeathTest`, switches on `OVERSEE_TEST` versus `EXECUTE_TEST`, waits and validates in the parent, executes the statement under a sentinel in the child, and streams `DeathTest::LastMessage()` on failure.
- `GTEST_EXECUTE_DEATH_TEST_STATEMENT_` wraps death-test statements in exception handling when exceptions are enabled and aborts the death test if exceptions escape.
- `ASSERT_EXIT`, `EXPECT_EXIT`, `ASSERT_DEATH`, `EXPECT_DEATH`, `EXPECT_DEBUG_DEATH`, `ASSERT_DEBUG_DEATH`, `EXPECT_DEATH_IF_SUPPORTED`, and `ASSERT_DEATH_IF_SUPPORTED` are public-facing death-test macros in this slice.
- `ExitedWithCode` and, on supported non-Windows/non-Fuchsia platforms, `KilledBySignal` are predicate functors for exit status validation.

### linked_ptr

- `linked_ptr_internal` maintains a circular linked list of all smart pointers sharing an object. `join_new()` starts a one-element ring, `join()` inserts into another ring under global `g_linked_ptr_mutex`, and `depart()` removes from the ring and returns whether the departing pointer was last.
- `linked_ptr<T>` owns a raw pointer collectively with other `linked_ptr` copies. Destruction/reset/assignment call `depart()` and delete when the last ring member leaves. This is used where pre-C++11 shared ownership is needed without depending on `shared_ptr`.
- `make_linked_ptr()` is a convenience wrapper around `linked_ptr<T>(ptr)`.

### Universal Printers

- `internal2::PrintBytesInObjectTo()` and `TypeWithoutFormatter<T, TypeKind>` implement last-resort formatting for unknown types, protobuf messages, integer-convertible types, and Abseil string-view-convertible types.
- `testing_internal::DefaultPrintNonContainerTo()` uses ADL plus the internal fallback `operator<<` so user-defined `operator<<` wins when available.
- `FormatForComparison<ToPrint, OtherOperand>` and `FormatForComparisonFailureMessage()` specialize C string formatting: raw pointers by default, actual string content when compared against string types.
- `DefaultPrintTo()` selects container, pointer, function-pointer, or other formatting using the container and pointer traits.
- `PrintTo()` overloads cover characters, booleans, C strings, wide strings, `std::string`, optional global string/wstring types, Abseil string views, `nullptr_t`, tuples, pairs, and raw arrays.
- `UniversalPrinter<T>`, `UniversalPrinter<T[N]>`, and `UniversalPrinter<T&>` format values, arrays, and references. Reference printing includes the address; terse printers omit reference addresses and print char/wchar pointers as strings.
- `UniversalPrintArray()` truncates long arrays by printing the first and last chunks; char and wchar arrays have compact overloads.
- `TuplePolicy`, `TuplePrefixPrinter`, `PrintTupleTo()`, and `UniversalTersePrintTupleFieldsToStrings()` bridge both TR1 and standard tuples.
- `PrintToString<T>()` is the public wrapper that returns terse formatting through a `stringstream`.

### Parameterized Test Internals

- `TestParamInfo<ParamType>` carries a parameter value plus its numeric index into user param-name generators.
- `PrintToStringParamName` names parameters using `PrintToString(info.param)`.
- `ParamIteratorInterface<T>`, `ParamIterator<T>`, `ParamGeneratorInterface<T>`, and `ParamGenerator<T>` define the iterator/generator abstraction used by all parameter sources. `ParamGenerator` shares immutable implementations through `linked_ptr`.
- `RangeGenerator<T, IncrementT>` generates `[begin, end)` by repeated `operator+` and `operator<`, computing `end_index_` up front so iterator comparison uses indexes.
- `ValuesInIteratorRangeGenerator<T>` copies an input iterator range into a `std::vector<T>` so generated tests can outlive stack-allocated input containers. Its iterator caches dereferenced values to support `operator->()` even when iterator dereference returns a temporary.
- `DefaultParamName`, `GetParamNameGen`, and `ParamNameGenFunc` select the default index-based naming function or a user-provided name generator.
- `ParameterizedTestFactory<TestClass>` stores one parameter, sets it on `TestClass` before construction, and creates the actual test instance.
- `TestMetaFactoryBase` and `TestMetaFactory<TestCase>` create fresh owned factories for each parameterized test instance.
- `ParameterizedTestCaseInfoBase` and `ParameterizedTestCaseInfo<TestCase>` accumulate `TEST_P` patterns and `INSTANTIATE_TEST_CASE_P` generator declarations, then register every test/generator/parameter combination in `RegisterTests()`.
- `ParameterizedTestCaseRegistry` stores all parameterized test case descriptors, verifies that repeated test case names use the same fixture type, and calls `RegisterTests()` on every descriptor.
- Generated `ValueArray1` through the start of `ValueArray15` implement polymorphic `Values(v1, ..., vN)` support. Each stores constructor arguments by value and converts to `ParamGenerator<T>` by building a local `T array[]` with `static_cast<T>(vi_)` and returning `ValuesIn(array)`.

## Control Flow

Typed-test registration is compile-time recursion expressed as static runtime registration calls. Macro expansion creates namespace-scope booleans or static pointers whose initializers call `Register()`/`MakeAndRegisterTestInfo()`. `TypeParameterizedTestCase` walks the list of test templates, and for each test, `TypeParameterizedTest` walks the list of types. Each leaf calls `MakeAndRegisterTestInfo()` with a generated case name containing optional prefix, case name, and type-name suffix.

Normal `TEST`/`TEST_F` flow is simpler: `GTEST_TEST_` declares a generated fixture subclass and statically registers a `TestFactoryImpl` for it. At run time, Google Test later calls the factory to create and destroy the test object.

Assertion macros use an `if/else` pattern with `GTEST_AMBIGUOUS_ELSE_BLOCKER_` and generated labels to support streaming syntax and avoid dangling-else issues. Exception assertions execute the statement under `try/catch`; boolean assertions convert the expression to `AssertionResult`; no-fatal-failure assertions snapshot the current thread's fatal-failure state with `HasNewFatalFailureHelper`.

Death-test flow is split by role. The overseeing process creates a concrete `DeathTest`, assumes `OVERSEE_TEST`, waits for the child, applies the user exit predicate, and evaluates captured stderr against the regex. The executing child assumes `EXECUTE_TEST`, runs the statement under `ReturnSentinel`, and aborts with a specific reason if the statement returns, throws, or fails to die. Unsupported death-test macros compile the statement/regex in an unreachable branch and emit a warning instead of executing the statement.

Parameterized tests are registered later, when the unit-test implementation asks the registry to register tests. `ParameterizedTestCaseInfo::RegisterTests()` nests loops over stored test patterns, instantiations, and generated parameters. It validates parameter names for non-empty alphanumeric/underscore content, rejects duplicates within an instantiation, builds names as `test_base_name/param_name`, and calls `MakeAndRegisterTestInfo()` with `value_param = PrintToString(*param_it)`.

Universal printing uses overload resolution first. `UniversalPrinter<T>::Print()` calls `PrintTo(value, os)` unqualified so user `PrintTo()` overloads found by ADL can override internal defaults. The generic internal `PrintTo()` then dispatches to container/pointer/function-pointer/other paths. If no user stream operator or printer exists, fallback formatting chooses protobuf debug strings, integer conversion, Abseil string view conversion, or raw bytes.

## State and Persistence Behavior

Most state in this chunk is process-local registration metadata held in static or registry-owned structures, not persisted to disk. Static initialization registers tests and type information before `RUN_ALL_TESTS()`. `ParameterizedTestCaseRegistry` owns dynamically allocated `ParameterizedTestCaseInfoBase` objects until destruction. `ParameterizedTestCaseInfo` owns test meta-factories and records instantiations as strings, function pointers, file names, and lines.

Death-test state includes `DeathTest::last_death_test_message_`, the parsed `internal_run_death_test` flag, and file descriptors used for parent/child communication. `InternalRunDeathTestFlag` is RAII for its write fd. Death tests may re-execute the binary in "threadsafe" style, so state observed by the child can differ from the parent except for command-line flag propagation and explicit IPC.

`linked_ptr` persists ownership state as an intrusive circular list among smart-pointer instances and uses a single global mutex for operations on all rings. `NativeArray` either holds a borrowed pointer or an owned heap copy, encoded by its `clone_` member function pointer. `RangeGenerator` and `ValuesInIteratorRangeGenerator` hold immutable copied parameter data so generators can be safely reused after the original input expression goes out of scope.

Floating-point helpers store raw value bits in a union. Printers and formatters are stateless except for local `stringstream`/vector accumulation.

## Dependencies and Integration Points

This chunk depends on earlier fused-header definitions for portability macros, `TypesN`/`TemplateSel`/`NoneT`, `Message`, `AssertionResult`, `TestPartResult`, `Test`, `UnitTest`, `scoped_ptr`, mutex primitives, type traits such as `AddReference`, `IteratorTraits`, `bool_constant`, and platform feature macros such as `GTEST_HAS_DEATH_TEST`, `GTEST_HAS_TYPED_TEST`, `GTEST_HAS_TR1_TUPLE`, `GTEST_HAS_STD_TUPLE_`, and `GTEST_HAS_ABSL`.

It integrates with later and external implementation units through `GTEST_API_` declarations: assertion message builders, diff functions, stack trace capture, random number generation, HRESULT predicates, death-test concrete factories, public string/wide-string printers, and parameterized-test invalid-type reporting are declared here but implemented elsewhere in the fused source.

Public user integration points include `TEST`, `TEST_F`, typed-test macros, death-test macros, parameterized-test macros, `ValuesIn`, `Values`, `Range`, `PrintToString`, user-defined `PrintTo(const T&, ostream*)`, user-defined `operator<<`, and param name generator functors. The code also optionally integrates with protobuf, Abseil `optional`/`variant`/`string_view`, TR1 tuples, standard tuples, Windows HRESULTs, and POSIX signal status semantics.

## Risks and Edge Cases

- The generated arity limits are hard-coded: typed templates and `Values` support up to 50 parameters in this file family, while `Combine` is documented as limited to 10. Calls beyond those limits require generated code outside this slice or will fail to compile.
- Static initialization order matters because test registration happens through namespace-scope variables. This is normal for Google Test, but unusual build/linker behavior can affect registration, which is why `GetTestTypeId()` has a special exported path.
- `linked_ptr` has known caveats: cycles leak, converting raw pointers back into new `linked_ptr` instances can double-delete, and assignment traverses a ring under one global mutex. This is acceptable for test metadata but risky as a general-purpose smart pointer.
- Death tests are platform-sensitive. Fork/thread interactions can be unsafe with multiple active threads; "threadsafe" style relies on `argv[0]` being a usable path; unsupported platforms only warn; child-side side effects are generally not visible in the parent.
- `GTEST_DEATH_TEST_` uses `goto` labels generated from `__LINE__`; macro use patterns that place multiple generated labels on one source line can be fragile.
- Universal printing can instantiate surprising overloads. Container detection is heuristic, recursive containers are suppressed, input iterators may print with inferred element types, and unknown types fall back to raw bytes, which may expose padding or implementation-specific representations.
- C string formatting intentionally changes depending on the comparison operand type. This improves string comparison diagnostics but can surprise users comparing raw pointers.
- `RangeGenerator::CalculateEndIndex()` assumes positive progress toward `end`; invalid `step` values or unusual `operator+`/`operator<` behavior can cause long or infinite loops.
- Parameterized test names must be unique and contain only alphanumeric characters or underscores. `PrintToStringParamName` can generate invalid names for many value types unless the printed form is sanitized by the user.
- `Values(...)` generated arrays use `static_cast<T>` for each stored argument, so narrowing, explicit conversions, or non-copyable parameter types can fail at compile time.
- This chunk ends before the full generated `ValueArray15` body and later `ValueArrayN` classes, so the merge lane should combine with following chunks before making whole-file conclusions about complete `Values` support.

## Test Signals

Good coverage for this chunk would come from compiling and running Google Test's own typed-test, type-parameterized-test, death-test, printer, and parameterized-test suites. Specific signals include:

- Typed-test cases with one type, multiple types, custom type-name generators, missing/extra registered names, and fixture type mismatches.
- `TEST`/`TEST_F` registration checks verifying fixture setup/teardown hooks and duplicate fixture class detection.
- Floating-point assertions around NaN, infinities, signed zero, values within four ULPs, and values outside tolerance.
- Death tests for `ASSERT_EXIT`, `EXPECT_EXIT`, `ASSERT_DEATH`, debug death behavior under both `NDEBUG` and non-`NDEBUG`, exception escaping from a death statement, unsupported-platform fallback compilation, and exit-by-signal predicates where available.
- Universal printer tests for user `PrintTo`, user `operator<<`, protobuf-like objects, enums, containers, recursive containers, hash containers, native arrays, char/wchar pointers, null pointers, function pointers, tuples, pairs, Abseil optional/variant/string_view, and unknown byte-formatted objects.
- Parameterized tests using `Range`, `ValuesIn` from stack arrays and containers, generated values with temporary dereference behavior, custom valid and invalid parameter names, duplicate names, multiple instantiations, and mismatched fixture classes across namespaces.

## Cross-Chunk Notes

Earlier chunks define the beginning of the `TemplatesN` and `TypesN` generated lists, core port/type traits, `Message`, `AssertionResult`, `Test`, and other prerequisites. Later chunks continue the generated `ValueArrayN` series and likely define the public `Values`, `Range`, `Bool`, `Combine`, `TEST_P`, and `INSTANTIATE_TEST_CASE_P` macro surfaces that consume the internals introduced here. This chunk should be merged as a middle slice of a single fused `gtest.h` report, not treated as an independent standalone header.

### subset-b-008690: lines 12680-18782

# sources/storage-engines/rocksdb/third-party/gtest-1.8.1/fused-src/gtest/gtest.h lines 12680-18782

## Scope

This chunk covers the generated value-parameter support in the fused Google Test 1.8.1 header embedded under RocksDB. It starts in the tail of `internal::ValueArray15`, continues through `internal::ValueArray16` through `internal::ValueArray50`, defines the generated Cartesian-product generator and holder classes used by `Combine()`, closes `gtest-param-util-generated.h`, and then begins the public parameter-generator factory functions in namespace `testing`.

The public factory section includes `Range()`, all `ValuesIn()` overloads, generated `Values()` overloads for 1 through 50 arguments, `Bool()`, and the beginning of `Combine()` overloads. The chunk ends on the return type for the public four-argument `Combine()` overload, so later `Combine()` overload bodies and the remainder of the header are outside this chunk.

## Purpose

- Provide source-level implementations for Google Test value-parameterized test generator helpers in the fused single-header distribution used by RocksDB's vendored test dependency.
- Let users write `Values(...)` with heterogeneous literal arguments and defer conversion until the expression is assigned to a concrete `ParamGenerator<T>`.
- Let users build `ParamGenerator<T>` instances from ranges, C arrays, STL containers, and iterator ranges.
- Let users generate Boolean parameter sequences with `Bool()`.
- When `GTEST_HAS_COMBINE` is enabled, let users combine two to ten parameter generators into a Cartesian product whose element type is `testing::tuple<T1, ..., TN>`.
- Avoid variadic templates by using generated fixed-arity classes and overloads, which keeps Google Test 1.8.1 compatible with older C++ compilers.

## Important APIs, Types, And Functions

- `internal::ValueArray15` through `internal::ValueArray50` are generated holder classes for the high-arity `Values()` implementation. Each stores constructor arguments in `const Tn vn_` members, supports copy construction, disables assignment by declaring a private unimplemented `operator=`, and exposes `template <typename T> operator ParamGenerator<T>() const`.
- Each `ValueArrayN::operator ParamGenerator<T>()` builds a local `const T array[]` by `static_cast<T>`-converting every stored value, then delegates to `ValuesIn(array)`. This gives `Values(1, 2, 3.5)` the ability to become a `ParamGenerator<double>`, `ParamGenerator<int>`, or another compatible target selected by the test fixture parameter type.
- `testing::Range(T start, T end, IncrementT step)` constructs `internal::RangeGenerator<T, IncrementT>`. The two-argument overload delegates to `Range(start, end, 1)`.
- `testing::ValuesIn(ForwardIterator begin, ForwardIterator end)` determines the parameter type with `internal::IteratorTraits<ForwardIterator>::value_type` and constructs `internal::ValuesInIteratorRangeGenerator<ParamType>`.
- `testing::ValuesIn(const T (&array)[N])` forwards to the iterator overload with `array` and `array + N`.
- `testing::ValuesIn(const Container& container)` forwards to the iterator overload with `container.begin()` and `container.end()`.
- `testing::Values()` overloads for arities 1 through 50 return the corresponding `internal::ValueArrayN<...>` holder. In this chunk, the source-visible overload list includes all arities and the high-arity tail from 15 through 50 aligns with the generated classes above.
- `testing::Bool()` is a convenience wrapper returning `Values(false, true)` as `internal::ParamGenerator<bool>`.
- `internal::CartesianProductGenerator2` through `internal::CartesianProductGenerator10` implement the concrete generator interfaces for `Combine()`. Each derives from `ParamGeneratorInterface<testing::tuple<...> >`, stores its input `ParamGenerator<Tn>` objects by value, and creates nested iterators from each input generator's begin/end positions.
- Each nested Cartesian `Iterator` implements `ParamIteratorInterface<ParamType>` methods: `BaseGenerator()`, `Advance()`, `Clone()`, `Current()`, and `Equals()`.
- `internal::CartesianProductHolder2` through `internal::CartesianProductHolder10` are polymorphic adapter holders returned by public `Combine()` overloads. They store the original generator expressions by value and convert later to `ParamGenerator<testing::tuple<T...> >` by statically converting each held expression to `ParamGenerator<Tn>` and allocating the matching `CartesianProductGeneratorN`.
- Public `testing::Combine()` overloads begin in this chunk. The two- and three-argument overloads are fully present, and the four-argument overload declaration begins at the chunk boundary.

## Control Flow

`Values(...)` is intentionally two-stage. A call such as `Values("a", "b")` returns a `ValueArray2<const char*, const char*>`, not an immediate concrete parameter generator. When Google Test instantiation needs a `ParamGenerator<T>`, the holder conversion operator runs, casts every saved value to `T`, places those converted values in a stack array, and calls `ValuesIn(array)`. `ValuesIn()` immediately constructs a `ValuesInIteratorRangeGenerator`, whose implementation elsewhere copies the values, so the local stack array is not retained after conversion.

`Range()` is direct: the public helper creates a `RangeGenerator` with the caller's start, end, and step. The generated sequence is documented as half-open and requires `start < end` for non-empty output. Runtime iteration logic for `RangeGenerator` lives earlier in the header, outside this chunk.

`ValuesIn()` overloads normalize three input styles into a begin/end iterator pair. The iterator overload deduces the value type and constructs a generator around the supplied range. The array overload uses pointer iterators, and the container overload uses STL-style iterators. The surrounding comments explicitly state that values are copied for use later during `RUN_ALL_TESTS()`.

When `GTEST_HAS_COMBINE` is enabled, `Combine(g1, g2, ...)` returns a `CartesianProductHolderN` expression. Like `Values()`, this holder is not the final typed generator. Its conversion operator selects tuple element types from the consuming context, converts each stored expression to `ParamGenerator<Tn>`, and allocates a `CartesianProductGeneratorN<T...>`.

Each `CartesianProductGeneratorN::Begin()` constructs an iterator with every component at its begin position. `End()` constructs one with every component at end. The nested iterator caches each component's `begin`, `end`, and current iterator. `Advance()` increments the last component first; when that component reaches end, it resets that component to begin and increments the previous component. This carry propagation repeats toward the first component, producing lexicographic Cartesian-product order with the rightmost generator varying fastest.

`ComputeCurrentValue()` materializes the current tuple in a `linked_ptr<ParamType>` whenever the iterator is not at end. `AtEnd()` returns true if any component iterator equals its corresponding end iterator. This is important for empty inputs: a Cartesian product with any empty component is immediately empty, and all exhausted combinations compare as end even if individual component states differ.

`Equals()` first checks that both iterators came from the same base generator pointer using `GTEST_CHECK_`. It then downcasts with `CheckedDowncastToActualType` and reports equality if both are logically at end or if every component current iterator is equal. This prevents accidental comparison between unrelated generator instances while still treating multiple exhausted states as the same end position.

## State And Persistence Behavior

This code does not persist RocksDB state and does not interact with RocksDB storage. It is part of the vendored test framework and affects only in-memory test registration and parameter generation.

The relevant state is test-generation state:

- `ValueArrayN` holders store copies of all `Values()` arguments as `const` members until conversion to a concrete `ParamGenerator<T>`.
- `ValuesIn()` generators copy range elements for later test execution, decoupling test parameters from temporary containers or stack arrays used during instantiation.
- `CartesianProductGeneratorN` stores input `ParamGenerator<Tn>` objects by value. Those generators own or share their own generator implementation objects according to Google Test's `ParamGenerator` wrapper semantics.
- Cartesian iterators store begin/end/current iterators for every input generator and a heap-allocated current tuple through `linked_ptr`. Cloned iterators recompute the tuple from copied component iterator positions.
- All generated holder and generator classes disable assignment, avoiding accidental member reassignment while still permitting copy construction where needed for expression passing and iterator cloning.

## Dependencies And Integration Points

- This chunk is inside `namespace testing` and `namespace testing::internal`, and depends on parameter-generator infrastructure defined earlier in `gtest.h`: `ParamGenerator`, `ParamGeneratorInterface`, `ParamIteratorInterface`, `RangeGenerator`, `ValuesInIteratorRangeGenerator`, `IteratorTraits`, and `linked_ptr`.
- Tuple support comes from Google Test's tuple implementation exposed as `testing::tuple`. `Combine()` is limited to ten inputs because this Google Test release's tuple implementation has that generated arity limit.
- Error checking and RTTI-like downcasting use internal helpers/macros including `GTEST_CHECK_` and `CheckedDowncastToActualType`.
- The entire Cartesian-product section and public `Combine()` helpers are guarded by `GTEST_HAS_COMBINE`. Builds without that feature still provide `Range()`, `ValuesIn()`, `Values()`, and `Bool()`.
- Public integration is through parameterized-test macros elsewhere in Google Test, especially `TEST_P`, `TestWithParam<T>`, and `INSTANTIATE_TEST_CASE_P`, which accept these generator expressions and convert them to typed `ParamGenerator<T>` objects.
- RocksDB integrates this only as a vendored third-party testing dependency. Production RocksDB storage-engine code should not depend on these APIs.

## Risks And Edge Cases

- This is generated, pre-variadic-template code. Any manual patch to one arity can leave other arities inconsistent, especially across `ValueArrayN`, `Values()` overloads, `CartesianProductGeneratorN`, `CartesianProductHolderN`, and `Combine()` overloads.
- `Values()` conversion uses `static_cast<T>` for every argument. Narrowing, lossy floating-point conversion, pointer conversion, or user-defined conversion side effects happen at generator conversion time, not at the original `Values()` call site.
- `ValueArrayN` stores values by value. Expensive objects are copied, and non-copyable argument types are not supported by this generated API shape.
- `ValuesIn(const Container&)` assumes the container has `value_type`, `begin()`, and `end()` members. It also relies on the range-copy behavior of `ValuesInIteratorRangeGenerator`; if that contract were changed, temporary containers passed to `ValuesIn(GetVector())` would become dangerous.
- Cartesian products grow multiplicatively. Large input generators can produce very large numbers of instantiated tests, increasing registration time, binary/test metadata size, and runtime.
- Empty component generators make the whole Cartesian product empty because `AtEnd()` checks every component. This is correct but can silently result in no parameterized tests for a suite if one input sequence is empty.
- `Advance()` asserts that the iterator is not already at end. Calling it on an exhausted iterator is a contract violation and would be caught only in assertion-enabled builds.
- `Equals()` aborts via `GTEST_CHECK_` if iterators from different base generators are compared. This is intentional but can surprise code that treats parameter iterators like ordinary STL iterators.
- The generated Cartesian iterators allocate a new tuple object each time `ComputeCurrentValue()` runs. Very large products can therefore allocate heavily during parameter enumeration.
- The chunk boundary cuts through public `Combine()` overload declarations. A source audit or patch touching `Combine()` must include the following chunk before drawing conclusions about all public arities.

## Test Signals

- Parameterized tests should confirm `Values()` supports representative low and high arities, including the generated high-arity range up to 50 arguments.
- Type-conversion tests should instantiate fixtures where `Values()` contains heterogeneous values and the fixture parameter type controls the final conversion.
- Lifetime tests should pass temporary arrays/containers/ranges through `ValuesIn()` and verify values remain available during `RUN_ALL_TESTS()`.
- `Range()` tests should cover half-open behavior, custom increments, floating-point or user-defined increment types, and empty ranges when `start < end` is false.
- `Bool()` tests should verify the generated sequence is exactly `false` followed by `true`.
- `Combine()` tests under `GTEST_HAS_COMBINE` should verify Cartesian order, especially that the rightmost generator varies fastest.
- Empty-product tests should combine non-empty generators with one empty generator and verify no parameter values are produced.
- Iterator tests should cover begin/end equality, cloned iterator equality, and exhaustion behavior where different component iterator states still compare as logical end.
- Negative tests or death tests can cover comparing iterators from different generator instances, which should trigger the `GTEST_CHECK_` path.
- Build tests should cover configurations with `GTEST_HAS_COMBINE` enabled and disabled, since the public API surface changes under that macro.

### subset-b-008691: lines 18783-22095

# sources/storage-engines/rocksdb/third-party/gtest-1.8.1/fused-src/gtest/gtest.h lines 18783-22095

## Scope

This chunk is the tail of the fused Google Test 1.8.1 public header embedded under RocksDB's third-party sources. It starts at the end of value-parameterized test support, including `Combine()` overloads and the `TEST_P` / `INSTANTIATE_TEST_CASE_P` registration macros. It then contains the fused `gtest_prod.h`, `gtest-test-part.h`, `gtest-typed-test.h`, generated predicate assertion macro header, and the final public `gtest.h` API surface through `RUN_ALL_TESTS()`.

The code is mostly declarations, inline helpers, and macros. Its behavior is completed by the compiled Google Test implementation elsewhere in the fused distribution, but this header defines the user-visible testing DSL, the test metadata model, event listener interfaces, assertion result plumbing, typed/value-parameterized registration hooks, and the singleton `UnitTest` interface used by RocksDB tests.

## Purpose

This range exposes the core Google Test contracts used by RocksDB's C++ test binaries:

- value-parameterized tests are declared with `TEST_P`, instantiated with `INSTANTIATE_TEST_CASE_P`, and can combine up to ten parameter generators when `GTEST_HAS_COMBINE` is enabled;
- production classes can grant friendship to a generated Google Test fixture class through `FRIEND_TEST`;
- individual assertion outcomes are represented as `TestPartResult` objects and delivered through `TestPartResultReporterInterface`;
- typed tests and type-parameterized tests register generated test classes for a list of types via `TYPED_TEST_CASE`, `TYPED_TEST`, `TYPED_TEST_CASE_P`, `TYPED_TEST_P`, `REGISTER_TYPED_TEST_CASE_P`, and `INSTANTIATE_TYPED_TEST_CASE_P`;
- global Google Test flags are declared for filtering, repetition, shuffling, XML output, exception handling, colored output, stack traces, disabled tests, and result streaming;
- `AssertionResult` provides rich Boolean/predicate assertion results with lazily allocated streamed messages;
- generated predicate assertion macros reduce `EXPECT_PRED*` and `ASSERT_PRED*` calls to `GTEST_ASSERT_`;
- `Test`, `TestResult`, `TestInfo`, `TestCase`, `Environment`, `TestEventListener`, `TestEventListeners`, and `UnitTest` describe the runtime test graph and lifecycle;
- public assertion macros map user code (`EXPECT_EQ`, `ASSERT_TRUE`, `SCOPED_TRACE`, etc.) onto internal helper functions and `AssertHelper`;
- `RUN_ALL_TESTS()` is the final global entry point that dispatches to `UnitTest::GetInstance()->Run()`.

## Important APIs, Types, And Macros

- `Combine()` overloads for arities 4 through 10 return `internal::CartesianProductHolderN` objects. They are part of value-parameterized test generator composition and depend on `GTEST_HAS_COMBINE`.
- `TEST_P(test_case_name, test_name)` creates a generated subclass of the parameterized fixture, registers a `TestMetaFactory` in `UnitTest::parameterized_test_registry()`, and leaves the user's test body as the generated `TestBody()` definition.
- `INSTANTIATE_TEST_CASE_P(prefix, test_case_name, generator, ...)` stores an evaluated `ParamGenerator<ParamType>` function and a test-name generator function, then registers the instantiation under the parameterized test case registry. The optional name generator is selected through `internal::GetParamNameGen`.
- `FRIEND_TEST(test_case_name, test_name)` expands to friendship for the generated `test_case_name_test_name_Test` class. This is a production-code hook used when tests need private or protected access.
- `TestPartResult` stores assertion outcome type, source file, line, summary, and full message. It distinguishes success, non-fatal failure, and fatal failure. It normalizes unknown file names to an empty string internally and returns `NULL` from `file_name()` when unknown.
- `TestPartResultArray` owns a `std::vector<TestPartResult>` and exposes append/index/size operations.
- `TestPartResultReporterInterface` is the reporting sink for assertion results. `internal::HasNewFatalFailureHelper` temporarily installs itself as the active reporter for `{ASSERT|EXPECT}_NO_FATAL_FAILURE`, delegates to the previous reporter, records whether a new fatal failure occurred, and restores the original reporter in its destructor.
- Typed-test macros synthesize generated fixture subclasses and registration state:
  - `GTEST_TYPE_PARAMS_` and `GTEST_NAME_GENERATOR_` create hidden typedef names.
  - `TYPED_TEST_CASE` builds an internal type list and selected name generator.
  - `TYPED_TEST` registers one test body for all types in a known type list.
  - `TYPED_TEST_CASE_P`, `TYPED_TEST_P`, `REGISTER_TYPED_TEST_CASE_P`, and `INSTANTIATE_TYPED_TEST_CASE_P` support abstract type-parameterized test patterns that are later instantiated by type list and prefix.
- Google Test flags declared here include `also_run_disabled_tests`, `break_on_failure`, `catch_exceptions`, `color`, `filter`, `install_failure_signal_handler`, `list_tests`, `output`, `print_time`, `print_utf8`, `random_seed`, `repeat`, `show_internal_stack_frames`, `shuffle`, `stack_trace_depth`, `throw_on_failure`, `stream_result_to`, and optionally `flagfile`.
- `AssertionResult` is copyable and contextually convertible to `bool`. It supports `operator!`, `message()`, deprecated `failure_message()`, and streaming through `operator<<`. Message storage uses `internal::scoped_ptr<std::string>` to keep common assertion stack usage small.
- `AssertionSuccess()`, `AssertionFailure()`, and deprecated `AssertionFailure(const Message&)` are factory functions for predicate results.
- Generated predicate helpers `AssertPred1Helper` through `AssertPred5Helper` build failure messages that include predicate text, expression text, and evaluated values. Public macros cover both raw Boolean predicates and predicate-format functions for arities 1 through 5.
- `Test` is the base fixture class. It exposes static `SetUpTestCase()`, `TearDownTestCase()`, failure query helpers, and `RecordProperty()`, while the private runtime path calls `SetUp()`, `TestBody()`, `TearDown()`, and `DeleteSelf_()`.
- `TestProperty` stores a key/value pair for XML output and supports value replacement for duplicate keys.
- `TestResult` owns assertion results, test properties, death-test count, and elapsed time. It exposes aggregate failure queries and indexed access, while friends mutate it during test execution.
- `TestInfo` stores immutable test identity and factory metadata plus mutable `TestResult`. It tracks whether a test should run, is disabled, matches filters, or belongs to another shard.
- `TestCase` owns `TestInfo` objects, setup/teardown function pointers, a shuffle indirection vector, per-test-case ad hoc properties, and elapsed time. It computes counts for successful, failed, disabled, reportable, runnable, and total tests.
- `Environment` is the base class for global setup/teardown hooks registered through `AddGlobalTestEnvironment()`.
- `AssertionException` is available when exceptions are enabled and wraps a `TestPartResult` for listeners that throw on assertion failure.
- `TestEventListener` defines the full event sequence from program start through iterations, environments, test cases, individual tests, assertion parts, and program end. `EmptyTestEventListener` supplies no-op overrides.
- `TestEventListeners` owns listener registration, default result printer, default XML generator, and an internal repeater used to broadcast events.
- `UnitTest` is the process-wide singleton. It runs tests, exposes current test/test case, aggregate counts, timing, random seed, ad hoc result, listeners, and the internal parameterized-test registry. Its mutable implementation state is protected by `internal::Mutex`.
- Comparison helpers include `CmpHelperEQ`, `EqHelper`, `CmpHelperNE/LE/LT/GE/GT`, C-string and wide-string comparison helpers, substring predicates, floating-point equality helpers, `DoubleNearPredFormat`, `FloatLE`, and `DoubleLE`.
- `AssertHelper` is the small assertion failure adapter used by failure macros to support streaming messages into assertions.
- `WithParamInterface<T>` exposes `GetParam()` for value-parameterized fixtures through a static `parameter_` pointer set by `internal::ParameterizedTestFactory`. `TestWithParam<T>` combines `Test` and `WithParamInterface<T>`.
- Public user macros include `ADD_FAILURE`, `ADD_FAILURE_AT`, `FAIL`, `SUCCEED`, exception assertions, Boolean assertions, equality/ordering assertions, string assertions, floating-point assertions, HRESULT assertions on Windows, no-fatal-failure assertions, `SCOPED_TRACE`, `GTEST_TEST`, `TEST`, and `TEST_F`.
- `ScopedTrace` pushes file/line/message trace context on construction and pops it on destruction; `SCOPED_TRACE` creates a unique local trace variable using the current line.
- `StaticAssertTypeEq<T1, T2>()` triggers a compile-time type equality check by instantiating `internal::StaticAssertTypeEqHelper`.
- `TempDir()` declares the platform-specific temporary-directory helper.
- `RUN_ALL_TESTS()` is declared in the global namespace and inlined to call the singleton `UnitTest` runner.

## Control Flow

Test registration in this chunk is mostly static initialization driven by macros. `TEST_P` expands into a generated test class and a static dummy integer initialized by `AddToRegistry()`. That initializer calls `UnitTest::GetInstance()->parameterized_test_registry()`, obtains the `ParameterizedTestCaseInfo` holder for the fixture, and adds a test pattern with a `TestMetaFactory`. `INSTANTIATE_TEST_CASE_P` similarly creates static helper functions for the generator and parameter-name generator, then registers an instantiation with source file and line metadata. The actual concrete tests are materialized later by the Google Test runtime before execution.

Typed-test registration follows a similar pattern but routes through type-list helpers. `TYPED_TEST_CASE` fixes the type list and name generator for a fixture template. Each `TYPED_TEST` defines a templated generated test class and invokes `internal::TypeParameterizedTest<...>::Register()` with the case name, test name, code location, and generated type names. Type-parameterized tests split the process: `TYPED_TEST_CASE_P` creates a static `TypedTestCasePState`, each `TYPED_TEST_P` records a test name in that state, `REGISTER_TYPED_TEST_CASE_P` verifies that the listed names match the definitions, and `INSTANTIATE_TYPED_TEST_CASE_P` registers all templates for the selected type list and prefix.

Assertion macros reduce to a common reporting path. Predicate macros call predicate helper functions or predicate-format functions, producing an `AssertionResult`. `GTEST_ASSERT_` tests that result, does nothing on success, and invokes either fatal or non-fatal failure handlers with the assertion message on failure. Equality and ordering assertions reuse predicate-format macros so expression text and evaluated values can be formatted consistently. Fatal assertions route through failure macros that abort the current function according to Google Test's internal fatal-failure mechanism; non-fatal assertions record a result and continue.

During execution, `RUN_ALL_TESTS()` calls `UnitTest::Run()`. `UnitTest` delegates to its internal implementation to select tests according to flags, sharding, disabled-state rules, and filters. It iterates test cases, runs per-case setup, creates each test through the `TestInfo` factory, calls `Test::Run()` to execute fixture setup/body/teardown, records results, fires listener events, runs per-case teardown, and aggregates counts and elapsed time. The public declarations here expose the metadata and listener interfaces; the detailed implementation lives outside this header.

`ScopedTrace` and `HasNewFatalFailureHelper` are RAII control-flow adapters. `ScopedTrace` pushes trace context into `UnitTest` on construction and pops on destruction so failures inside the lexical scope include additional context. `HasNewFatalFailureHelper` temporarily replaces the current test-part reporter, watches delegated assertion results for fatal failures, and restores the previous reporter in its destructor, allowing `EXPECT_NO_FATAL_FAILURE` and `ASSERT_NO_FATAL_FAILURE` to test a statement's side effects on the failure stream.

## State And Persistence Behavior

The state in this header is process-local Google Test runtime state, not RocksDB on-disk persistence. Persistent storage in the application sense is not performed here. Important stateful behavior includes:

- `UnitTest` is a singleton created on first use and intentionally never deleted; it owns the global test registry, implementation object, listener set, environments, current-test pointers, result state, and flag-derived run configuration.
- Static initialization produced by `TEST`, `TEST_F`, `TEST_P`, typed-test macros, and instantiate macros registers test metadata before `main()` calls `RUN_ALL_TESTS()`. Linkage and initialization order are therefore part of the test discovery model.
- `TestCase` owns `TestInfo` pointers, preserves original test order, and maintains `test_indices_` so shuffling can be undone.
- `TestInfo` owns its factory pointer and contains a `TestResult` that must be cleared before repeated runs.
- `TestResult` accumulates `TestPartResult` entries, properties, death-test count, and elapsed time; property mutation is protected by `test_properites_mutex_` because duplicate keys update existing values.
- `WithParamInterface<T>::parameter_` is a static pointer per parameter type. The parameterized-test factory sets it for the lifetime of a running value-parameterized test; `GetParam()` checks that it is non-null and returns a const reference.
- `AssertionResult` lazily allocates a message string only when a caller streams diagnostic text into it.
- Listener ownership transfers to Google Test when appended to `TestEventListeners`; `Release()` transfers ownership back to the caller.
- Global environments registered with `AddGlobalTestEnvironment()` are owned by the `UnitTest` singleton, set up in registration order, and torn down in reverse order.
- Test properties recorded by `Test::RecordProperty()` are routed to the current test result, current test case ad hoc result, or global ad hoc result depending on where the call occurs.

The only file-related API declared here is `TempDir()` and XML/output flag plumbing. The actual XML report generation and temporary-directory resolution are implemented elsewhere.

## Dependencies And Integration Points

This chunk depends on the rest of fused Google Test for internal macros, type traits, containers, mutexes, factories, and implementations. It references `internal::UnitTestImpl`, `internal::ParameterizedTestCaseRegistry`, `internal::TypeParameterizedTest`, `internal::TypeParameterizedTestCase`, `internal::TypedTestCasePState`, `internal::NameGeneratorSelector`, `internal::TemplateSel`, `internal::Templates`, `internal::TypeList`, `internal::GenerateNames`, `internal::CodeLocation`, `internal::TypeId`, `internal::TestFactoryBase`, `internal::SetUpTestCaseFunc`, `internal::TearDownTestCaseFunc`, `internal::Random`, `internal::TraceInfo`, `internal::Mutex`, `internal::scoped_ptr`, and many assertion helper macros defined earlier in the same fused header.

The public integration point for RocksDB test code is broad. RocksDB tests include this header to define tests, fixtures, parameterized tests, typed tests, global environments, listeners, assertions, and `main()` bodies. `FRIEND_TEST` can also appear in production headers to expose internals to specific generated test classes. Because the header is vendored under RocksDB's third-party tree, changing it affects compilation of all tests that include RocksDB's bundled Google Test rather than a system-provided copy.

Platform integration appears through conditional macros. Windows-only HRESULT assertions depend on Windows SDK HRESULT conventions. Exception-specific APIs depend on `GTEST_HAS_EXCEPTIONS`. Wide-string substring helpers depend on `GTEST_HAS_STD_WSTRING`. Global `::string` support depends on `GTEST_HAS_GLOBAL_STRING`. `GTEST_DISABLE_MSC_WARNINGS_PUSH_` / `POP_` wrap declarations to quiet MSVC DLL-interface and unused-parameter warnings. `GTEST_DONT_DEFINE_*` switches allow users to avoid generic macro names such as `TEST`, `FAIL`, `SUCCEED`, and `ASSERT_EQ` when they conflict with other libraries.

The event listener interfaces are the main extension hooks for custom output, XML suppression/replacement, streaming results, failure behavior, and integration with external test harnesses. `UnitTest::listeners()` exposes the listener collection, while `UnitTest::parameterized_test_registry()` is documented as internal but is required by public parameterized-test macros.

## Risks And Edge Cases

- Static registration depends on object initialization across translation units. Parameterized and typed test patterns placed in headers can register in multiple translation units, so the macros use `static` state carefully; changing linkage or registration names can create duplicate, missing, or order-dependent tests.
- `TEST_P` and typed-test macros synthesize class names. User fixture names, test names, and `FRIEND_TEST` declarations must match those generated names exactly, including namespace placement.
- `INSTANTIATE_TEST_CASE_P` test-name generators must return non-empty, unique names containing only ASCII alphanumeric characters or underscore. The default `PrintToStringParamName` is not suitable for strings because quoting can create invalid names.
- `WithParamInterface<T>::parameter_` is a static pointer, not an owned value. The factory must guarantee parameter lifetime and must reset or replace it correctly for each running test.
- `GetParam()` intentionally checks that the parameter pointer is set; calling it from a fixture used with `TEST_F` instead of `TEST_P` trips a runtime check.
- Assertion macros note that argument evaluation order is undefined, even though each argument is evaluated once. Tests with side effects in assertion arguments can still be non-portable.
- Equality assertions compare C string pointers rather than string contents; tests must use `EXPECT_STREQ` and related macros for C-string content checks.
- `EqHelper<true>` has specialized overloads for null pointer literals to avoid bad overload resolution and compiler warnings. Refactoring null handling can reintroduce ambiguous overloads or `-Wconversion-null` warnings.
- `AssertionResult` supports implicit Boolean usage but uses a templated constructor guarded by `ImplicitlyConvertible` to avoid stealing copy construction. Changes to this overload set can break predicate assertion ergonomics or compiler compatibility.
- `TestResult::GetTestPartResult()` and `GetTestProperty()` abort on invalid indexes according to comments; callers should treat counts as authoritative.
- `TestEventListener::OnTestPartResult()` may throw only `AssertionException` or a subclass when using exceptions to skip to the next test. Throwing arbitrary exceptions from listeners risks undefined framework behavior.
- `UnitTest::Run()` and `AddEnvironment()` are documented as main-thread-only. Calling them from worker threads can race against runtime state despite some accessors being mutex protected.
- `ScopedTrace` assumes per-thread trace stacks. Cross-thread assertions are not automatically annotated by traces created in another thread.
- `StaticAssertTypeEq()` only fires when the containing template/function is instantiated, so unused template methods can hide type mismatches.
- The field name `test_properites_mutex_` is misspelled in this vendored version. External code should not depend on private names, but local patches should avoid accidental "cleanup" that changes ABI or conflicts with upstream.
- Fused generated predicate macros are limited to arity 5 in this version. Tests needing larger predicate arity must compose checks or use custom assertion helpers.

## Test Signals

This file is itself test infrastructure, so direct signals are primarily compile-time and framework-behavior signals from all tests that include it:

- successful compilation of ordinary tests using `TEST` and `TEST_F` confirms generated class names, fixture inheritance, and factory registration remain valid;
- value-parameterized tests using `TEST_P`, `INSTANTIATE_TEST_CASE_P`, `GetParam()`, `Range`, `Values`, `ValuesIn`, `Bool`, and `Combine` validate parameter registry, generator evaluation, parameter lifetime, and generated names;
- typed and type-parameterized tests validate type-list expansion, type-name generation, registration verification, and instantiation prefixes;
- assertion-heavy tests validate `AssertionResult`, predicate helpers, comparison helpers, fatal/non-fatal result reporting, message streaming, and source location capture;
- tests using `EXPECT_NO_FATAL_FAILURE` and `ASSERT_NO_FATAL_FAILURE` validate temporary reporter replacement and restoration;
- tests with `SCOPED_TRACE` validate trace stack push/pop and failure message annotation;
- listener customizations validate event ordering, listener ownership, default printer/XML generator release, and result forwarding;
- tests using `RecordProperty()` and XML output validate property routing to test, test-case, or global result scopes;
- shuffling, filtering, disabled tests, repeat counts, random seeds, exception handling, and XML/output flags validate the `UnitTest` run configuration exposed by this header.

For RocksDB specifically, regressions in this chunk usually surface as broad test binary compile failures, missing or duplicated tests, parameterized test instantiation errors, assertion messages losing useful diagnostics, incorrect fatal/non-fatal behavior, listener/XML output changes, or runtime failures in tests that depend on `FRIEND_TEST`, `SCOPED_TRACE`, or `TestWithParam`.
