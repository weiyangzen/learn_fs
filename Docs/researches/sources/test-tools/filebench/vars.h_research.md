# `sources/test-tools/filebench/vars.h`

Purpose: Defines Filebench variable and attribute descriptor types and declares the variable/AVD API used by parser and runtime code.

Important APIs and types: `avd_type_t` distinguishes inline bool/int/double/string values, variable-backed typed pointers, unknown variable references, random variables, and custom variables. `struct avd` stores the selected type plus a union of direct values and pointers. `var_type_t` and `var_t` represent named variables with typed union storage and list linkage. Macros classify and set variable/AVD types. Public functions allocate AVDs, assign variables, resolve typed AVD values, update local variables, and stringify variables or random parameters.

Control flow and integration: Workload parsing uses `avd_*_alloc()` and `avd_var_alloc()` to attach attributes to process/thread/flowop definitions. Runtime code calls typed getters when it needs the current value. Assignment APIs back the f-language `set` command and random/custom variable setup.

State and persistence: The header describes objects allocated in Filebench shared memory, allowing values to be visible across process-mode worker instances. Variable values persist for a workload lifetime.

Dependencies: Includes `filebench.h` and forward references `randdist` and `cvar` objects through struct pointers.

Risks and test signals: Macros are multi-statement blocks without `do { } while (0)`, so use in conditional contexts can be unsafe. Typing is enforced at runtime, not compile time. Tests should include parser integration, macro use under normal call sites, and all typed getter conversions.
