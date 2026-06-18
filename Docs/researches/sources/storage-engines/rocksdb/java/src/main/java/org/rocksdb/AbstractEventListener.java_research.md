# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractEventListener.java

## Purpose
This base class lets Java code implement RocksDB event listeners. It provides no-op implementations for all listener callbacks, optional callback selection, and private JNI proxy methods that wrap native DB handles into Java objects without transferring ownership.

## Important APIs, Types, and Functions
`AbstractEventListener` extends `RocksCallbackObject` and implements `EventListener`. The nested `EnabledEventCallback` enum maps callback names to byte values and supports `fromValue`. Constructors either enable all callbacks or pack selected callbacks into a bitmask. It implements no-op listener methods for flush, compaction, table file, memtable, column-family handle deletion, external ingestion, background error, stall, file IO, error recovery, and recovery completion. Proxy methods include `onFlushCompletedProxy`, `onFlushBeginProxy`, `onCompactionBeginProxy`, `onCompactionCompletedProxy`, `onExternalFileIngestedProxy`, `onBackgroundErrorProxy`, and `onErrorRecoveryBeginProxy`. Native methods create and dispose the native listener.

## Control Flow
Construction packs selected enum values into a long bitmask and passes it through `RocksCallbackObject` initialization. Native code invokes private proxy methods for callbacks needing a temporary `RocksDB` wrapper or enum conversion. Proxies create wrappers from native DB handles, call `disOwnNativeHandle` to avoid deleting non-owned DBs, and dispatch to overridable public methods. Default public implementations are no-ops or return conservative defaults.

## State and Persistence Behavior
The listener stores native callback state through `RocksCallbackObject`. It does not persist data directly, but callbacks observe and can respond to persistence-related events such as flush, compaction, file IO, background errors, and recovery. Error recovery callbacks can influence continuation by returning a boolean.

## Dependencies and Integration Points
It integrates with `EventListener`, `RocksDB`, many event info DTOs, `BackgroundErrorReason`, `Status`, and native event listener callback code. The enablement bitmask allows native code to avoid calling unneeded Java callbacks.

## Risks and Edge Cases
Enum byte values are part of the native contract and must stay synchronized with C++ callback dispatch. The default constructor enables all callbacks, which may be expensive; the selective constructor is preferred for performance. Temporary DB wrappers must always disown native handles to avoid double-free. Callback exceptions and threading behavior are handled in native code outside this file.

## Test Signals
Tests should verify bitmask packing for selected callbacks, `fromValue` validation, dispatch for each proxy and no-op method, handle disowning, background/error recovery enum conversion, and disposal of the native listener.
