<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/Program.cs -->
# sources/user-network-fs/smblibrary/SMBServer/Program.cs

## Purpose
WinForms sample application entry point for the SMB server UI, with global exception handling.

## APIs, Types, and Functions
`Main()` is marked `[STAThread]`, subscribes to `Application.ThreadException` and `AppDomain.CurrentDomain.UnhandledException`, enables visual styles, and runs `ServerUI`. Helper handlers call `HandleUnhandledException()`.

## Control Flow, State, and Persistence
Unhandled UI or domain exceptions are formatted into a message box and then `Application.Exit()` is called. No persistent state is written.

## Dependencies and Integration
Starts the `ServerUI` form. Depends on Windows Forms and threading exception events.

## Risks and Test Signals
Risks include casting `UnhandledExceptionEventArgs.ExceptionObject` directly to `Exception`, showing stack traces to users, and no logging of fatal errors if UI cannot display. Test startup, UI-thread exceptions, background exceptions, and graceful application exit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/Program.cs -->
