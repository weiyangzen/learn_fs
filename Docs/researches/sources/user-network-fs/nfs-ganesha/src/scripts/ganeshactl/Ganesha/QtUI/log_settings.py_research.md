# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/log_settings.py

## Purpose

`log_settings.py` implements the GUI log-settings dialog. It presents Ganesha log components in an editable table and pushes changed levels back over DBus.

## Important APIs, Types, and Functions

`DebugLevelDelegate` creates a combo-box editor containing log levels from `log_levels_t`. `LogSettingsModel` fetches component levels through `LogManager.GetAll`, stores `[component, level]` rows, exposes editable column 1, and calls `LogManager.Set` after edits. `LogSetDialog` wires the generated `Ui_LogSettings` dialog, the model, the delegate, and the Done button.

## Control Flow

The dialog constructs a table model and delegate, installs them on `log_levels`, fetches current components, then connects the model's `dataChanged` signal to `updateSetting`. `getComponents_done` sorts returned component names and populates rows without calling `setData`, avoiding accidental writeback. User edits in the level column flow through `DebugLevelDelegate.setModelData`, then `LogSettingsModel.setData`, then `updateSetting`, which calls `Set` and refreshes all components.

## State and Persistence Behavior

Dialog state is transient in `self.log_components`. Persistent effects are remote: edits change live Ganesha DBus log properties. The dialog itself only hides on Done and remains reusable.

## Dependencies and Integration Points

It depends on PyQt5 and generated `Ganesha.QtUI.ui_log_dialog.Ui_LogSettings`. It integrates with `Ganesha.log_mgr.LogManager` in the GUI process and with the server's `org.ganesha.nfsd.log.component` DBus property interface.

## Risks and Edge Cases

The file imports widgets from `QtGui` even though many moved to `QtWidgets` in PyQt5. It uses `xrange`, `QVariant`, and `index.data(...).toString()`, which are PyQt4-era idioms. `removeRows` references `self.log_comp_levels`, a nonexistent attribute, and computes the removal range as `count + count - 1`; removal paths can fail. Any edit immediately writes to the daemon, so validation of level names depends on the combo-box list and DBus backend.

## Test Signals

Tests should use a fake log manager emitting component dictionaries, verify sorted row population, simulate delegate edits, and assert `Set(component, level)` plus refresh calls. Import/UI smoke tests under PyQt5 are high value because several widget APIs are version-sensitive.
