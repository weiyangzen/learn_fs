# sources/storage-engines/foundationdb/flow/include/flow/Buggify.h

Purpose: implements deterministic probabilistic fault-injection gates for simulation/testing.

Important APIs/types/functions: `P_EXPENSIVE_VALIDATION`, `BuggifySection`, `BuggifySectionHash`, generated general/client buggify globals and functions, `_buggify`, macros `EXPENSIVE_VALIDATION`, `CLIENT_BUGGIFY_WITH_PROB`, `CLIENT_BUGGIFY`, `buggify`, and Swift bridging helpers.

Control flow: each source file/line section is activated once based on deterministic random and cached in a map. If enabled and activated, individual calls fire based on another probability. Activation is added to `g_traceBatch` and dumped when `g_network` exists.

State/persistence: inline global probabilities and section maps store process-wide buggify state. Swift bridging uses a `std::map` keyed by string/line.

Dependencies/integration: deterministic random, Trace batching, global `g_network`, Swift bridging namespace. Used pervasively in simulation to inject rare behavior.

Risks: `BuggifySection` hashes/equality compare `const char*` file pointer identity, not string contents, while Swift uses string keys. Header inline globals are process-global and not thread-protected. Probabilities are mutable globals.

Test signals: simulation runs with general/client buggify enabled and trace batch records of activated sections.
