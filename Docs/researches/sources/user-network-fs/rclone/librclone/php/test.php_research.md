# sources/user-network-fs/rclone/librclone/php/test.php

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/php/test.php -->
## sources/user-network-fs/rclone/librclone/php/test.php

Purpose: demonstration/test script for the PHP FFI wrapper using a configured remote.

Important APIs and control flow: the script constructs `Rclone`, lists remotes, creates a folder on `gdrive:/`, lists the remote, writes a local test file, copies it to the remote folder through `operations/copyfile`, lists the folder, checks the first listed item name, prints `SUCCESS` or `FAIL`, and closes the library.

State, dependencies, and integration: depends on `rclone.php`, `librclone.so`, PHP FFI, a configured `gdrive:/` remote, and local filesystem write access.

Risks and test signals: it is environment-dependent and can mutate a real remote. It is useful as an integration example but unsuitable as a hermetic unit test. It does not clean up the remote test folder/file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/php/test.php -->
