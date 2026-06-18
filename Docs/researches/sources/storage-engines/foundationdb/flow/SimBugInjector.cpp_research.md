<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/SimBugInjector.cpp -->
# sources/storage-engines/foundationdb/flow/SimBugInjector.cpp
- Purpose: Provides simulation-only injectable bug hooks keyed by bug identifier type.
- Important APIs/types/functions: `ISimBug`, `IBugIdentifier`, `SimBugInjector::enable`, `disable`, `reset`, `getImpl`, and `enableImpl`. `ISimBug::hit()` logs and dispatches `onHit()`.
- Control flow: `enable()` asserts the network is simulated, lazily creates global state, and sets the enabled flag. `enableImpl()` looks up the identifier type and creates the bug object through `id.create()` if missing. `getImpl()` returns existing bugs only when the injector exists and, unless requested, is enabled.
- State and persistence behavior: `simBugInjector` is a heap global containing an enabled flag and `unordered_map<type_index, shared_ptr<ISimBug>>`. `ISimBugImpl` tracks hit counts per bug. `reset()` deletes the global but does not null the pointer in the observed code, so callers must treat reset use carefully.
- Dependencies and integration points: Depends on `g_network->isSimulated()`, `TraceEvent`, RTTI, `boost::core::demangle`, and bug identifier subclasses elsewhere in simulation code.
- Risks: It can intentionally corrupt behavior and is guarded against non-simulation use. The apparent missing null assignment after `delete simBugInjector` is a dangling-pointer risk if reset is followed by further injector access. Type-index identity makes ABI and RTTI consistency important.
- Test signals: Simulation tests should verify enable/disable/get paths, hit count logging, demangled names, and reset behavior. Non-simulation enable should assert.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/SimBugInjector.cpp -->
