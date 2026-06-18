# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/LoopThread.cpp

## Purpose
Implements threading helpers: a left-right wait-free-read structure, named loop threads, thread-system restart around fork, and platform thread naming. This specific file has 31 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `: _loopIteration(std::move(loopIteration)), _runningHandle(none), _threadName(std::move(threadName)) {`; `LoopThread::~LoopThread() {`; `if (_runningHandle != none) {`; `stop();`; `void LoopThread::start() {`; `_runningHandle = ThreadSystem::singleton().start(_loopIteration, _threadName);`; `void LoopThread::stop() {`; `if (_runningHandle == none) {`; `throw std::runtime_error("LoopThread is not running");`; `ThreadSystem::singleton().stop(*_runningHandle);`. CMake commands used here include `if`, `stop`. Primary includes/dependencies visible in the file include `LoopThread.h`, `../logging/logging.h`.

## Control Flow
Thread helpers start named boost threads, repeatedly invoke a loop callback until it returns false or interruption occurs, and stop/restart managed threads around fork on non-Windows platforms.

## State and Persistence Behavior
ThreadSystem stores a process-wide list of running threads and callbacks so it can interrupt, join, and restart them around fork.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `LoopThread.h`, `../logging/logging.h`.

## Risks and Edge Cases
Thread interruption and fork restart are timing-sensitive. Callbacks must tolerate interruption points and should not hold locks across fork boundaries.

## Test Signals
Test loop start/stop, no double stop, thread naming, LeftRight concurrent reads/writes, and ThreadSystem fork restart behavior on non-Windows.
