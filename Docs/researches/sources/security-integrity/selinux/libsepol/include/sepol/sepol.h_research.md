# sources/security-integrity/selinux/libsepol/include/sepol/sepol.h

Purpose: Provides an umbrella public header for libsepol records, collections, handles, debugging, policydb, modules, and contexts.

Important APIs and symbols: Includes all major public record and collection headers plus `sepol_set_policydb_from_file(FILE *fp)`.

Control flow: External callers include this single header to access the public libsepol API. `sepol_set_policydb_from_file` initializes internal service state from a file.

State and persistence: The umbrella itself has no state. The service initializer affects process-global internal policydb state used by service calls.

Dependencies and integration points: Central downstream integration point for C and C++ callers, with `extern "C"` wrapping.

Risks: Pulling many headers increases compile coupling. Global service initialization should be avoided in code requiring isolation.

Test signals: Installed-header compilation from C and C++, and service initialization from a valid policy file, validate the umbrella.
