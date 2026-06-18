# sources/storage-engines/sqlite/tool/GetFile.cs

## Purpose
`GetFile.cs` is a small C# command-line tool that downloads one URI to the process temporary directory. It is a build/support helper for environments where SQLite scripts need to fetch a single external file with progress reporting and deterministic exit codes.

## Important APIs, Types, and Functions
`ExitCode` enumerates success and failure causes. `Program.Error()` prints usage and optional diagnostics. `Program.GetFileName()` extracts the final path segment from a URI. `DownloadProgressChanged()` serializes progress output with `syncRoot` and prevents percentage regression. `DownloadFileCompleted()` records `DownloadCanceled` or `DownloadError`, prints final status, and signals `doneEvent`. `Main()` validates arguments, resolves URI and output name, configures TLS 1.2 through `ServicePointManager.SecurityProtocol`, uses `WebClient.DownloadFileAsync()`, and waits on a `ManualResetEvent`.

## Control Flow
The entry point accepts `<uri> [fileName]`. It requires an absolute URI, chooses either the basename of the optional filename or the URI path basename, verifies `Path.GetTempPath()`, deletes any existing temp file with that basename, starts an async download, and blocks until the completion event fires. Event handlers update progress and final exit state.

## State and Persistence
Persistent state is the downloaded file under the process temp directory. Global process state includes the static `doneEvent`, `previousPercent`, and `exitCode`; these are safe for the single-download process model. The tool also changes the process `ServicePointManager.SecurityProtocol` to TLS 1.2.

## Dependencies and Integration Points
The file uses .NET Framework-era APIs from `System.Net`, `System.Threading`, `System.IO`, and diagnostics/reflection namespaces. It integrates with SQLite build scripts as a standalone executable and reports failures by numeric process exit code.

## Risks
The output is forced into the temp directory and strips directory components from the optional file name, so callers cannot choose an arbitrary destination. Existing files with the same temp basename are deleted without prompting. `WebClient` and the hard-coded TLS numeric constant are legacy .NET patterns. The async workflow waits forever and has no timeout. URI-derived filenames include the full `PathAndQuery` suffix after the final slash, so unusual query strings can produce awkward names.

## Test Signals
Test with valid HTTP/HTTPS URIs, invalid URIs, URI paths without filenames, explicit filenames containing directories, unavailable temp directories where possible, existing temp files, and network failures. Progress should be monotonic and final exit codes should match the `ExitCode` enum.
