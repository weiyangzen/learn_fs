# sources/user-network-fs/nfs-ganesha/src/tracing/CMakeLists.txt

Purpose: this CMake file builds and installs Ganesha's optional LTTng tracing module and exposes weak-symbol tracepoint support for other targets.

Important targets and APIs: it includes `${LTTNG_INCLUDE_DIR}`, builds `ganesha_trace` as a `MODULE` from `lttng_probes.c`, applies `add_sanitizers()`, and links `${LTTNG_LIBRARIES}`. It also defines `ganesha_trace_symbols` as an `INTERFACE` library that contributes `lttng_defines.c` to consumers and links LTTng libraries. `gsh_trace_header_generate` depends on `ntirpc_generate_lttng_trace_headers` and `gsh_generate_lttng_trace_headers`.

Control flow: generated trace headers are made prerequisites of both the loadable module and interface symbol target via `add_dependencies()`. Installation places `ganesha_trace` in `${LIB_INSTALL_DIR}` under component `tracing`.

State and persistence: build outputs are CMake target artifacts; no runtime state is handled here.

Dependencies and integration points: this file integrates CMake, LTTng discovery variables, sanitizer helpers, and generated trace header targets elsewhere in the project. Consumers that call tracepoints should link `ganesha_trace_symbols`; runtime tracing loads the module.

Risks: missing generated-header target definitions or unset LTTng variables will break configuration/build. Since `ganesha_trace` is a module, runtime loader paths and install component packaging need validation. The interface source pattern is unusual but intentional for weak tracepoint definitions.

Test signals: configure with `USE_LTTNG`, build both targets, verify generated headers run first, confirm linked consumers resolve tracepoint weak symbols without loading the module, and install/package the tracing component.
