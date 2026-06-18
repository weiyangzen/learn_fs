# sources/user-network-fs/rclone/cmd/authorize/authorize_test.go

Purpose: focused test for the authorize command's public help/usage surface. It asserts the `Use` string exactly matches the expected argument form and executes `authorize --help` through a throwaway Cobra parent command, checking the help output mentions `authorize <backendname>`.

State is in-memory command output buffer only. Dependencies are testing, strings, bytes, and Cobra. The test guards documentation/CLI UX but does not execute OAuth authorization, browser suppression, template rendering, or config writes. It is useful for preventing accidental regression of the argument synopsis.
