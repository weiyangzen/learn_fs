# sources/security-integrity/fsverity-utils/scripts/run-sparse.sh

Purpose: This script runs the Sparse static analyzer over fsverity-utils C sources with project include paths and build defines.

Important APIs and steps: It invokes `sparse` on library and program sources, supplying headers and flags needed to parse Linux-style annotations and UAPI structures.

Control flow and state: The script is stateless apart from analyzer output and process status. CI treats nonzero exit as failure.

Dependencies and integration points: Called by the GitHub Actions workflow and developer checks. Depends on the `sparse` binary, C headers, and Makefile-compatible flags.

Risks and test signals: Sparse availability and flag drift can create false negatives or false positives. Signals are clean analyzer runs and caught address-space/type warnings before runtime tests.
