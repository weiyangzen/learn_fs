# sources/sync-backup/rsync/lib/dummy.in

Purpose: build-system placeholder that ensures the `lib` directory is created by configure when building from a VPATH tree.

Important APIs/types/functions: no APIs, types, or functions.

Control flow: no executable control flow; the file is build input data only.

State and persistence behavior: no runtime state. Its persistence is the presence of the file in the source tree so generated/configure output has a concrete directory member to copy or instantiate.

Dependencies/integration: used by the configure/build process, especially VPATH builds where empty directories may otherwise be absent.

Risks/test signals: risk is accidental deletion causing VPATH/configure directory creation regressions. Build tests should include an out-of-tree configure run.
