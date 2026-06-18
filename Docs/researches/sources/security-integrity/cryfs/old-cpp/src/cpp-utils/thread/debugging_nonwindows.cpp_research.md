# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/debugging_nonwindows.cpp

## Purpose
Implements threading helpers: a left-right wait-free-read structure, named loop threads, thread-system restart around fork, and platform thread naming. This specific file has 105 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `OpenFileRAII`. Important declarations or call sites include `void set_thread_name(const char* name) {`; `std::string name_(name);`; `if (name_.size() > MAX_NAME_LEN - 1) {`; `name_.resize(MAX_NAME_LEN - 1);`; `int result = pthread_setname_np(name_.c_str());`; `int result = pthread_setname_np(pthread_self(), name_.c_str());`; `if (0 != result) {`; `throw std::runtime_error("Error setting thread name with pthread_setname_np. Code: " + std::to_string(result));`; `explicit OpenFileRAII(const char* filename) : fd(::open(filename, O_RDONLY | O_CLOEXEC)) {}`; `~OpenFileRAII() {`. CMake commands used here include `if`, `ASSERT`. Primary includes/dependencies visible in the file include `debugging.h`, `stdexcept`, `thread`, `pthread.h`, `cpp-utils/assert/assert.h`, `errno.h`, `fcntl.h`, `unistd.h`, `boost/filesystem/path.hpp`, `sys/types.h`.

## Control Flow
Thread helpers start named boost threads, repeatedly invoke a loop callback until it returns false or interruption occurs, and stop/restart managed threads around fork on non-Windows platforms.

## State and Persistence Behavior
ThreadSystem stores a process-wide list of running threads and callbacks so it can interrupt, join, and restart them around fork.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `debugging.h`, `stdexcept`, `thread`, `pthread.h`, `cpp-utils/assert/assert.h`, `errno.h`, `fcntl.h`, `unistd.h`.

## Risks and Edge Cases
Thread interruption and fork restart are timing-sensitive. Callbacks must tolerate interruption points and should not hold locks across fork boundaries.

## Test Signals
Test loop start/stop, no double stop, thread naming, LeftRight concurrent reads/writes, and ThreadSystem fork restart behavior on non-Windows.
