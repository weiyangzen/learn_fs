# sources/user-network-fs/libsmb2/.github/workflows/codeql.yml

Purpose: This workflow runs GitHub CodeQL analysis for C/C++ on master pushes, master pull requests, and a weekly Tuesday schedule.

Important APIs and types: It uses `github/codeql-action/init@v3`, `github/codeql-action/analyze@v3`, the `cpp` language matrix, `+security-and-quality` queries, and a manual CMake build step. Permissions are narrowed to read actions/contents and write security events.

Control flow: The job checks out the repository, initializes CodeQL for the matrix language, runs `cmake -S . -B build` and `cmake --build build`, then uploads analysis results with category `/language:cpp`.

State and persistence behavior: CodeQL's database and build outputs are transient within the workflow. Persistent output is the security alert data stored by GitHub's code scanning service.

Dependencies and integration points: The analysis path relies on the default CMake configuration being buildable on Ubuntu without extra packages beyond the runner image. It complements the broader `ccpp.yml` build matrix by adding static-analysis findings for the normal Linux CMake path.

Risks: CodeQL coverage follows only the default build options, so optional examples, platform-specific targets, and many conditional code paths are not analyzed. If CMake starts requiring packages not present on Ubuntu runners, analysis will fail before scanning.

Test signals: A successful run means CodeQL could trace the compiled C/C++ database. Findings in GitHub code scanning are the main output, especially security-and-quality alerts for memory, bounds, unchecked return values, and resource lifetime issues.
