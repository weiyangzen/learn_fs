# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFactory.cc

## Purpose
`XrdClHttpFactory.cc` implements the plugin factory entry point and global runtime initialization for the XrdCl HTTP plugin. It lazily sets environment defaults, starts the shared handler queue and curl workers, configures timeouts and credentials, and returns plugin `File` and `Filesystem` objects.

## Important APIs and Functions
`Factory::GetHeaderTimeoutWithDefault` maps operation timeouts to `timespec`. `Initialize` runs once under `m_init_once`. `SetupX509` imports certificate/proxy environment defaults. `Monitor` writes periodic JSON monitoring to logs and optionally an atomically replaced stats file. `Shutdown` joins the monitor thread. `Produce` enqueues an operation. `CreateFile`, `CreateFileSystem`, and `extern "C" XrdClGetPlugIn` expose the plugin to XRootD.

## Control Flow
Initialization gets the default logger/environment, registers the `XrdClHttp` log topic, imports environment variables, validates queue/thread/stall/slow-rate settings, parses header timeout defaults, initializes the OPTIONS cache singleton, starts `CurlWorker` threads, and starts the monitor thread. Shutdown is triggered by a static destructor and signals the monitor condition variable.

## State and Persistence
Static process-wide state includes initialized flag, shared `HandlerQueue`, log pointer, init flag, stats location, start time, shutdown mutex/CV/thread, and shutdown flag. Monitoring may persist JSON by writing a temporary file and renaming it over `HttpStatisticsLocation`.

## Dependencies and Integration Points
The file integrates XrdCl plugin interfaces, default environment, logging, version export macros, HTTP file/filesystem classes, curl worker utilities, timeout parsing, X509 environment conventions, and POSIX file APIs.

## Risks and Test Signals
Global lazy initialization and shutdown races are the main risk. `SetupX509` declares `disable_proxy` but never reads the imported value back, so `HttpDisableX509` may not disable proxy probing. Tests should cover fork-before-init behavior, invalid environment values, stats-file write failures, repeated plugin create calls, shutdown during initialization, and X509 fallback precedence.
