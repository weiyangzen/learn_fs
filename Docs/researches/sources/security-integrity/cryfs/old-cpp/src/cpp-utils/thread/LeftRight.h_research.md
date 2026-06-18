# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/LeftRight.h

## Purpose
Implements threading helpers: a left-right wait-free-read structure, named loop threads, thread-system restart around fork, and platform thread naming. This specific file has 162 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `IncrementRAII`, `T`, `LeftRight`, `F`. Important declarations or call sites include `explicit IncrementRAII(std::atomic<int32_t> *counter): _counter(counter) {`; `~IncrementRAII() {`; `DISALLOW_COPY_AND_ASSIGN(IncrementRAII);`; `~LeftRight() {`; `std::unique_lock<std::mutex> lock(_writeMutex);`; `while (_counters[0].load() != 0 || _counters[1].load() != 0) {`; `std::this_thread::yield();`; `auto read(F&& readFunc) const {`; `detail::IncrementRAII _increment_counter(&_counters[_foregroundCounterIndex.load()]); // NOLINT(cppcoreguidelines-pro-bounds-co...`; `if(_inDestruction.load()) {`. CMake commands used here include `DISALLOW_COPY_AND_ASSIGN`, `while`, `if`, `_callWriteFuncOnBackgroundInstance`, `_waitForBackgroundCounterToBeZero`. Primary includes/dependencies visible in the file include `atomic`, `functional`, `mutex`, `thread`, `cpp-utils/macros.h`, `array`, `stdexcept`.

## Control Flow
Thread helpers start named boost threads, repeatedly invoke a loop callback until it returns false or interruption occurs, and stop/restart managed threads around fork on non-Windows platforms.

## State and Persistence Behavior
ThreadSystem stores a process-wide list of running threads and callbacks so it can interrupt, join, and restart them around fork.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `atomic`, `functional`, `mutex`, `thread`, `cpp-utils/macros.h`, `array`, `stdexcept`.

## Risks and Edge Cases
Thread interruption and fork restart are timing-sensitive. Callbacks must tolerate interruption points and should not hold locks across fork boundaries.

## Test Signals
Test loop start/stop, no double stop, thread naming, LeftRight concurrent reads/writes, and ThreadSystem fork restart behavior on non-Windows.

## File-Specific Notes
- The left-right structure provides wait-free reads by duplicating data and using reader counters while writes update both copies under a mutex.
