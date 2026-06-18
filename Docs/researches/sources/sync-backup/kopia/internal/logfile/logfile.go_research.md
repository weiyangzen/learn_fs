# sources/sync-backup/kopia/internal/logfile/logfile.go

Purpose: attaches CLI flags and configures console, CLI file, and content log output for Kopia with rotation, sweeping, formatting, and cache-directory markers.

Important APIs/types/functions: `loggingFlags`, `Attach`, `setup`, `initialize`, `setupConsoleCore`, `setupLogFileBasedLogger`, `setupLogFileCore`, `jsonOrConsoleEncoder`, `shouldSweepLog`, `sweepLogDir`, `logLevelFromFlag`, and `onDemandFile` methods `Write`, `Sync`, `closeSegmentAndSweep`.

Control flow: `setup` registers kingpin flags and a pre-action initializer. `initialize` computes timestamp/suffix, builds zap cores for console and file logs, optionally creates content log writer, and installs the logger factory on the CLI app. File logging creates directories, cache markers, an on-demand segmented writer, and sweep callbacks. `onDemandFile.Write` opens the next segment lazily, rotates before overflow, updates `latest.log`, and writes bytes.

State/persistence behavior: persists log files under `cli-logs` and `content-logs`, with mode `0700` directories and cache markers. Sweeping removes old log files by count, aggregate size, or age, excluding nonmatching files and cache markers.

Dependencies/integration: depends on Kingpin, zap/zapcore, Kopia CLI app, cachedir/ospath/zaplogutil, and repository logging. It is attached to CLI test runners and real command startup.

Risks/test signals: log sweeping runs asynchronously unless configured to wait, so race windows exist around file listing. Symlink creation is best-effort. Size-based sweeping uses sorted newest-first cumulative size and can delete many segments when budgets shrink.
