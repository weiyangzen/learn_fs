<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClRecorderPlugin.hh -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClRecorderPlugin.hh

Purpose: declares and mostly implements `XrdCl::RecorderFactory`, the plugin factory that configures recorder output and creates `Recorder` file plugins.

Important APIs/types/functions: constructor reads config key `output` and calls `Recorder::SetOutput()`; `CreateFile()` constructs a `Recorder`, checks `IsValid()`, and returns it as `FilePlugIn`; `CreateFileSystem()` logs unsupported status and returns null.

Control flow: plugin load constructs the factory. The first created recorder triggers singleton output opening through `Recorder` construction. Invalid output setup causes `CreateFile()` to return null instead of a plugin.

State/persistence: no members in the factory. It causes process-global recorder output path state to be set through `Recorder::SetOutput()`.

Dependencies/integration: depends on `XrdClPlugInInterface` and on `Recorder` being visible from `XrdClRecorder.hh` before this header's inline constructor and `CreateFile()` are compiled.

Risks/test signals: output configuration is global, so multiple factory instances with different output paths can race or override before output opens. `CreateFileSystem()` uses `Log` and `DefaultEnv` names that must be available through included XrdCl headers. Tests should cover missing `output`, invalid paths, returning null on invalid output, and unsupported filesystem plugin reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClRecorderPlugin.hh -->
