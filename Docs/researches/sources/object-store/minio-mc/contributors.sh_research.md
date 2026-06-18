## sources/object-store/minio-mc/contributors.sh

Purpose: regenerates `CONTRIBUTORS.md` from git commit authors. The script changes to the repository directory, writes a fixed markdown header, then appends unique sorted `git log --format='%aN <%aE>'` entries as bullets.

Control flow is linear under `set -e`; any git/sort/sed failure aborts. State and persistence are the generated `CONTRIBUTORS.md` file in the mc repo. Dependencies are bash, `readlink -f`, git history, UTF-8 sort, and sed. Integration point is release or maintenance automation; it relies on `.mailmap` for author normalization. Risks include portability because `readlink -f` is not universal on macOS, and generated output depends on complete git history. Test signal is operational, not unit-tested.
