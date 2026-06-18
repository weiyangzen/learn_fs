# sources/user-network-fs/sshfs/test/meson.build

Purpose: Meson test subdirectory definition for sshfs tests and helper files.

Important APIs/types/functions: `test_scripts` list includes pytest config, `test_sshfs.py`, `test_hostname_validation.py`, and `util.py`; `custom_target` copies them into the build dir; builds `wrong_command` helper from C; registers `test('wrong_cmd', wrong_cmd)`.

Control flow: during build, test scripts are copied preserving metadata; Meson also builds and can run the `wrong_cmd` test target.

State and persistence behavior: creates copied test files and helper executable in the build directory.

Dependencies and integration points: links source tests to build-tree pytest invocations used by CI.

Risks: the file list must stay in sync with test additions. The custom target copies rather than generating a package manifest, so omitted tests may not run from build dir.

Test signals: Meson build target completion and `ninja test` wrong-command helper behavior.
