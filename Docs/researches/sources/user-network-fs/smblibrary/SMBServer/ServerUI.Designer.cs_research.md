<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/ServerUI.Designer.cs -->
# sources/user-network-fs/smblibrary/SMBServer/ServerUI.Designer.cs

## Purpose
WinForms designer-generated layout for the sample SMB server control panel.

## APIs, Types, and Functions
Partial class `ServerUI` defines `Dispose()` and `InitializeComponent()`, plus controls for IP address selection, transport radio buttons, start/stop buttons, integrated authentication, SMB1/SMB2 checkboxes, and labels.

## Control Flow, State, and Persistence
`InitializeComponent()` creates controls, sets fixed positions/sizes/text/default states, wires `Click`, `CheckedChanged`, and `Load` event handlers, and configures a fixed-size form. UI state is in WinForms controls; no persistence.

## Dependencies and Integration
Pairs with `ServerUI.cs` logic. Depends on `System.Windows.Forms` and `System.Drawing`.

## Risks and Test Signals
Risks include fixed non-scaled layout, no localization, SMB2 checkbox text limited to 2.0/2.1 despite optional SMB3 support in the library, and designer edits being overwritten. Test form loading, event wiring, tab order, high-DPI display, and enabled/disabled state transitions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/ServerUI.Designer.cs -->
