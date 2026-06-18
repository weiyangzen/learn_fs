# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/contract/AbstractContractLeaseRecoveryTest.java

Purpose: `AbstractContractLeaseRecoveryTest` validates lease recovery support for filesystems that advertise `CommonPathCapabilities.LEASE_RECOVERABLE`. It checks successful recovery on a closed file and strict failures on missing paths or directories.

Important APIs/types/functions: extends `AbstractFSContractTestBase`; uses `FileSystem`, `LeaseRecoverable`, `Path`, `FileNotFoundException`, AssertJ, JUnit `assertThrows`, and `ContractTestUtils.touch`. Helper `verifyAndGetLeaseRecoverableInstance` asserts both path capability and Java type compatibility before casting the filesystem to `LeaseRecoverable`.

Control flow: `testLeaseRecovery` touches a method path, verifies capability/type, calls `recoverLease(path)`, and asserts it returns true. It then asserts `isFileClosed(path)` returns true. `testLeaseRecoveryFileNotExist` uses a relative missing path and requires `FileNotFoundException` containing "File does not exist" for both methods. `testLeaseRecoveryFileOnDirectory` targets the parent directory of a method path and requires `FileNotFoundException` containing "Path is not a file".

State and persistence behavior: the positive case uses a closed zero-byte file, so recovery is expected to be idempotently successful rather than forcing active-writer recovery. The negative cases validate namespace type checks, not lease state mutation.

Dependencies and integration points: integrates the Hadoop lease recovery interface with path capability reporting. Concrete Ozone filesystems must expose both the capability and `LeaseRecoverable` interface consistently.

Risks and test signals: catches capability/type mismatch, lease APIs succeeding on missing paths or directories, incorrect exception type/message for invalid targets, and false negative recovery on closed files. It does not simulate a crashed writer or active lease contention.
