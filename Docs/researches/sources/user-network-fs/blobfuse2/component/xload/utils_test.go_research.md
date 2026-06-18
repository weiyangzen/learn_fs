## sources/user-network-fs/blobfuse2/component/xload/utils_test.go

Purpose: Unit tests for xload utility functions and mode enum behavior.

Important APIs and flow: `TestModeParse` checks case-insensitive parsing for valid modes plus errors for invalid values. `TestModeString` validates enum string names. `TestRoundFloat` checks several precision cases. `TestIsFilePresent` validates missing path, current directory detection, empty file detection, and size after truncate.

State and dependencies: Creates a temporary file in the current working directory and removes it with defer. Uses testify suite/assert and real filesystem metadata.

Risks and test signals: The temporary filename is fixed (`testFile1234`) inside the package working directory, so parallel package tests could collide. Rounding test expectations include `5.20`, which is numerically equal to `5.2`. Coverage is focused and adequate for utility contracts.
