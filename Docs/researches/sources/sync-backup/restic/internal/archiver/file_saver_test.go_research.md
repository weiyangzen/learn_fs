# sources/sync-backup/restic/internal/archiver/file_saver_test.go

Purpose: Focused concurrency test for `fileSaver`.

Important APIs and functions: `createTestFiles` creates temporary files. `startFileSaver` sets up an errgroup, random chunker polynomial, `mockSaver`, and a `NodeFromFileInfo` bridge. `TestFileSaver` queues multiple files through `Save`, waits on all futures, and validates that the mock saver saw every file.

Control flow and state: The test starts one worker per CPU, submits 15 files, consumes `futureNodeResult` values, shuts down the saver, and waits for worker exit.

Dependencies and integration: Uses `chunker.RandomPolynomial`, `fs.NewLocal`, `mockSaver` from `tree_saver_test.go`, `errgroup`, and the real `fileSaver` implementation.

Risks and test signals: It mainly signals queue/worker/future correctness under concurrent use. Broader file content, stats, and failure cases are covered by `archiver_test.go`.
