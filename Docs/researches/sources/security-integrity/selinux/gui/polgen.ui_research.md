# sources/security-integrity/selinux/gui/polgen.ui

## Purpose

`polgen.ui` is a GtkBuilder UI definition for the SELinux Policy Generation Tool. It defines the wizard-like interface used by `selinux-polgengui` to gather application/user type, executable/name, transition roles, network permissions, common capabilities, managed files/directories, booleans, and output directory.

## Important Objects And Signals

Top-level objects include `about_dialog`, `boolean_dialog`, `filechooserdialog`, and `main_window`. The main window contains a left-positioned `GtkNotebook` with tabs hidden, making it behave as a wizard controlled by `back_button`, `forward_button`, and `cancel_button`.

Important input widgets include policy type radio buttons (`init_radiobutton`, `dbus_radiobutton`, `inetd_radiobutton`, `cgi_radiobutton`, `user_radiobutton`, `sandbox_radiobutton`, user role radio buttons, and `root_user_radiobutton`), entries such as `exec_entry`, `name_entry`, `init_script_entry`, network port entries, `output_entry`, tree views for existing users/transitions/admins/roles/write paths/booleans, and checkboxes for TCP/UDP permissions and common access such as syslog, tmp, pam, uid, dbus, audit, terminal, and mail.

Signals bind several buttons to controller methods expected in the Python code: `on_exec_select_clicked`, `on_init_script_select_clicked`, `on_add_clicked`, `on_add_dir_clicked`, `on_delete_clicked`, `on_add_boolean_clicked`, and `on_delete_boolean_clicked`.

## Control Flow

The UI itself is declarative. Runtime flow is driven by the controller loading this file, advancing the hidden-tab notebook, reading widget state, and handling button signals. The layout starts with policy type selection, moves through name/executable selection and role/domain choices, then collects inbound/outbound network rules, common permissions, managed file paths, booleans, and output directory.

## State And Persistence

Widget state is transient until the controller generates policy files. The file chooser allows multiple hidden file selections. Text labels are marked translatable where user-facing. No persistent policy state is stored in this XML.

## Dependencies And Integration Points

The file depends on GTK/GtkBuilder object classes from the older GTK stack (`GtkVBox`, `GtkHBox`, `GtkTable`, stock buttons/images). It integrates with `polgengui.py` or equivalent controller code through exact object IDs and signal handler names, and with gettext through translatable properties.

## Risks

The UI is large and ID-sensitive; renaming widgets breaks controller lookups. It uses deprecated GTK classes and stock items, which can complicate GTK version migration. Hidden notebook tabs make controller navigation correctness important. Several labels contain `%s` placeholders, so controller code must set them safely and translators must preserve placeholders.

## Test Signals

UI tests should load the file with GtkBuilder, assert all controller-required object IDs and signal handlers exist, navigate every notebook page, and verify that tree views/buttons/entries needed by policy generation can be accessed. Translation checks should validate placeholder preservation in marked strings.
