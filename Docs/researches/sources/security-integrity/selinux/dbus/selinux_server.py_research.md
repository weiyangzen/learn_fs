# sources/security-integrity/selinux/dbus/selinux_server.py

## Purpose

`selinux_server.py` implements the privileged root-side `org.selinux` D-Bus service used by SELinux configuration tools. It exposes methods for exporting/importing semanage customizations, listing modules, restoring labels, changing enforcement, scheduling relabel, and editing default SELinux config values.

## Important APIs, Types, And Methods

The `selinux_server` class subclasses `dbus.service.Object`. `default_polkit_auth_required` is set to `org.selinux.semanage`, though each method performs explicit authorization through `is_authorized(sender, action_id)`. `is_authorized()` calls `org.freedesktop.PolicyKit1.Authority.CheckAuthorization` for the sender's system bus name.

D-Bus methods include `semanage(buf)`, `customized()`, `semodule_list()`, `restorecon(path)`, `setenforce(value)`, `relabel_on_boot(value)`, `change_default_mode(value)`, and `change_default_policy(value)`. Helper `write_selinux_config(enforcing=None, policy=None)` rewrites `selinux.selinux_path() + "config"` via a `.bck` file and `os.rename()`.

## Control Flow

At startup the script sets `DBusGMainLoop`, creates a GLib main loop, acquires `org.selinux` on the system bus, exports `/org/selinux/object`, and runs forever.

Each method first checks PolicyKit authorization for its specific action ID. Command-backed methods use `Popen`: `semanage()` runs `/usr/sbin/semanage import` with caller-provided input, `customized()` runs `/usr/sbin/semanage export`, and `semodule_list()` runs `/usr/sbin/semodule --list=full`. Direct libselinux-backed methods call `selinux.restorecon()` and `selinux.security_setenforce()`. Config methods validate input and rewrite config.

## State And Persistence

Persistent effects include semanage local policy store changes, module listing reads, filesystem relabeling, runtime enforcing mode changes, creation/removal of `/.autorelabel`, and edits to SELinux config. `write_selinux_config()` preserves unrelated config lines and atomically replaces the original path after writing a backup path.

## Dependencies And Integration Points

The server depends on Python D-Bus bindings, GLib main loop integration, PolicyKit, libselinux Python bindings, `/usr/sbin/semanage`, `/usr/sbin/semodule`, and the D-Bus/PolicyKit/service metadata in the same directory. GUI and client tools can use its D-Bus API instead of invoking privileged commands directly.

## Risks

The service runs as root, so authorization coverage and input validation are critical. `semanage()` passes arbitrary import text to semanage after authorization; this is expected but powerful. `restorecon()` accepts any path and runs recursively. `setenforce()` does not restrict integer values before passing to libselinux. `write_selinux_config()` does not preserve file mode/ownership explicitly and has no fsync/error recovery. PolicyKit errors are not handled separately from denial. `change_default_policy()` restricts names with a regex and requires a directory, which is a useful boundary.

## Test Signals

Tests should mock PolicyKit and command execution to verify authorization gates, command arguments, error propagation, and config rewrite behavior. Integration tests should verify installed action IDs, D-Bus method signatures, denial for unauthorized callers, and successful changes for authenticated admin callers in a controlled SELinux test environment.
