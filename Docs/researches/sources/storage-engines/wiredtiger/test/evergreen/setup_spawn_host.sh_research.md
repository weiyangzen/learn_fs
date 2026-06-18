<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/setup_spawn_host.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/setup_spawn_host.sh

Purpose: prepares an Evergreen spawn host for debugging a WiredTiger task by unpacking artifacts, configuring debugger paths, installing/finding CMake, setting shell environment, and notifying the user.

Control flow: starts in `$HOME`, notifies logged-in users with `wall`, creates `/data/wiredtiger` and symlinks it, extracts the first non-compile artifact tarball, checks for cores, and if present reads old source path from `CMakeCache.txt` and appends GDB `solib-search-path`, `substitute-path`, pretty printing, and safe path settings. It sources `find_cmake.sh`, appends PATH/LD_LIBRARY_PATH to `~/.profile`, writes `.bash_profile` helpers, then uses Evergreen credentials and AWS instance metadata to send a Slack message with SSH command.

State and persistence: mutates home directory, `/data/wiredtiger`, shell profiles, and `~/.gdbinit`.

Dependencies and integration: spawn-host setup task. Depends on artifacts in `/data/mci`, toolchain path, AWS metadata service, Evergreen CLI, and user credentials.

Risks and test signals: many commands assume Linux/AWS. Existing `wiredtiger` symlink/directory handling is not defensive. Slack notification is best effort when user lookup exists; setup completion is also broadcast with `wall`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/setup_spawn_host.sh -->
