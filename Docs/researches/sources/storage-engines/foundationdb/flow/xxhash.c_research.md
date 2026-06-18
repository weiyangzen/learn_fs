# sources/storage-engines/foundationdb/flow/xxhash.c

Purpose: This C file instantiates the xxHash implementation used by Flow by defining the implementation macros before including `flow/xxhash.h`. It provides the compiled function bodies for xxHash's header-defined algorithms.

Important APIs and types: The file enables `XXH_STATIC_LINKING_ONLY` for advanced declarations and `XXH_IMPLEMENTATION` for definitions, then includes `flow/xxhash.h`. The exported surface is determined by that header, not by this file.

Control flow: There is no local control flow beyond preprocessing. Compilation of this translation unit materializes the hashing functions for the rest of the binary.

State and persistence behavior: Hashing state is managed by xxHash functions and caller-provided state objects; this file stores no persistent state. The behavior must remain deterministic across supported platforms for checksums and hash-table uses.

Dependencies and integration points: It vendors Yann Collet's xxHash under BSD terms into the Flow build. It is linked wherever Flow needs fast non-cryptographic hashing.

Risks: Macro configuration drift can accidentally hide advanced APIs or duplicate definitions if another translation unit also defines `XXH_IMPLEMENTATION`. Tests should cover known xxHash vectors, static/dynamic linking modes, and any Flow code that persists or compares xxHash outputs.
