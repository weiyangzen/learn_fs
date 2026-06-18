# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/LoopThread.h

## Purpose
Implements threading helpers: a left-right wait-free-read structure, named loop threads, thread-system restart around fork, and platform thread naming. This specific file has 32 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `destructor`, `LoopThread`. Macros/constants: `MESSMER_CPPUTILS_THREAD_LOOPTHREAD_H`. Important declarations or call sites include `LoopThread(std::function<bool()> loopIteration, std::string threadName);`; `~LoopThread();`; `void start();`; `void stop();`; `DISALLOW_COPY_AND_ASSIGN(LoopThread);`. CMake commands used here include `LoopThread`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `ThreadSystem.h`, `boost/optional.hpp`.

## Control Flow
Thread helpers start named boost threads, repeatedly invoke a loop callback until it returns false or interruption occurs, and stop/restart managed threads around fork on non-Windows platforms.

## State and Persistence Behavior
ThreadSystem stores a process-wide list of running threads and callbacks so it can interrupt, join, and restart them around fork.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `ThreadSystem.h`, `boost/optional.hpp`.

## Risks and Edge Cases
Thread interruption and fork restart are timing-sensitive. Callbacks must tolerate interruption points and should not hold locks across fork boundaries.

## Test Signals
Test loop start/stop, no double stop, thread naming, LeftRight concurrent reads/writes, and ThreadSystem fork restart behavior on non-Windows.
