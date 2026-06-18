# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/ThreadSystem.cpp

## Purpose
Implements threading helpers: a left-right wait-free-read structure, named loop threads, thread-system restart around fork, and platform thread naming. This specific file has 113 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `ThreadSystem &ThreadSystem::singleton() {`; `ThreadSystem::ThreadSystem(): _runningThreads(), _mutex() {`; `pthread_atfork(&ThreadSystem::_onBeforeFork, &ThreadSystem::_onAfterFork, &ThreadSystem::_onAfterFork);`; `ThreadSystem::Handle ThreadSystem::start(function<bool()> loopIteration, string threadName) {`; `boost::unique_lock<boost::mutex> lock(_mutex);`; `auto thread = _startThread(loopIteration, threadName);`; `return std::prev(_runningThreads.end());`; `void ThreadSystem::stop(Handle handle) {`; `boost::unique_lock<boost::mutex> lock(_mutex);`; `boost::thread thread = std::move(handle->thread);`. CMake commands used here include `pthread_atfork`, `singleton`, `for`, `if`, `while`, `LOG`. Primary includes/dependencies visible in the file include `ThreadSystem.h`, `../logging/logging.h`, `debugging.h`.

## Control Flow
Thread helpers start named boost threads, repeatedly invoke a loop callback until it returns false or interruption occurs, and stop/restart managed threads around fork on non-Windows platforms.

## State and Persistence Behavior
ThreadSystem stores a process-wide list of running threads and callbacks so it can interrupt, join, and restart them around fork.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `ThreadSystem.h`, `../logging/logging.h`, `debugging.h`.

## Risks and Edge Cases
Thread interruption and fork restart are timing-sensitive. Callbacks must tolerate interruption points and should not hold locks across fork boundaries.

## Test Signals
Test loop start/stop, no double stop, thread naming, LeftRight concurrent reads/writes, and ThreadSystem fork restart behavior on non-Windows.

## File-Specific Notes
- Non-Windows builds register `pthread_atfork` hooks that interrupt managed threads before fork and restart them afterward.
