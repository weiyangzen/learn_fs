# File Research: sources/os/plan9/9front/sys/src/cmd/rio/rio.c

Main `rio` window manager. Handles startup, display/mouse/keyboard initialization, menus, snarf integration, keyboard tap routing, mouse event routing, window resize/move/sweep, hide/unhide, screen resize, child shell startup, and shutdown.

Creates windows around shell processes, tracks current/input windows, routes mouse/keyboard events to window channels, and exposes controls through the filesystem server.

Button menus implement New/Resize/Move/Delete/Hide/Exit and Cut/Paste/Snarf/Plumb/Look/Send/Scroll. Screen resize rescales existing windows and preserves z order.
