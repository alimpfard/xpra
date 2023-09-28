#!/usr/bin/env python3

import sys

import gi
gi.require_version('Gtk', '3.0')  # @UndefinedVariable
from gi.repository import Gtk    #pylint: disable=wrong-import-position @UnresolvedImport
from xpra.util.env import envbool


class StatusIcon:
    def __init__(self, name="test", tooltip="StatusIcon Example"):
        self.name = name
        self.statusicon = Gtk.StatusIcon()
        self.counter = 0
        self.statusicon.set_name(name)
        self.statusicon.set_from_stock(Gtk.STOCK_HOME)
        self.statusicon.connect("popup-menu", self.popup_menu)
        self.statusicon.connect("activate", self.activate)
        self.statusicon.set_tooltip_text(tooltip)
        #build list of stock icons:
        self.stock = {}
        try:
            nc = []
            if envbool("XPRA_NATIVE_NOTIFIER", True):
                from xpra.platform.gui import get_native_notifier_classes
                nc += get_native_notifier_classes()
            from xpra.gtk.notifier import GTK_Notifier
            nc.append(GTK_Notifier)
            self.notifier = nc[0](self.notification_closed, self.notification_action)
            self.notifier.app_name_format = "%s"
            #ensure we can send the image-path hint with the dbus backend:
            if hasattr(self.notifier, "noparse_hints"):
                self.notifier.parse_hints = self.notifier.noparse_hints
        except Exception as e:
            import traceback
            traceback.print_stack()
            print("Failed to instantiate the notifier: %s" % e)
        self.nid = 1
        for x in dir(Gtk):
            if x.startswith("STOCK_"):
                self.stock[x[len("STOCK_"):]] = getattr(Gtk, x)

    def activate(self, *_args):
        self.counter += 1
        name, stock = list(self.stock.items())[self.counter % len(self.stock)]
        print("setting tray icon to: %s" % name)
        self.statusicon.set_from_stock(stock)

    def popup_menu(self, icon, button, time):
        menu = Gtk.Menu()
        quit_menu = Gtk.MenuItem("Quit")
        quit_menu.connect("activate", Gtk.main_quit)
        menu.append(quit_menu)
        notify_menu = Gtk.MenuItem("Send Notification")
        notify_menu.connect("activate", self.notify)
        menu.append(notify_menu)
        menu.show_all()
        menu.popup(None, None, Gtk.StatusIcon.position_menu, self.statusicon, button, time)

    def notification_closed(self, nid, reason, text):
        print("notification_closed(%i, %i, %s)" % (nid, reason, text))

    def notification_action(self, nid, action):
        print("notification_action(%s, %s)" % (nid, action))

    def notify(self, *_args):
        actions = ["0", "Hello", "1", "Goodbye"]
        hints = {
            "image-path"    : "/usr/share/xpra/icons/encoding.png",
            }
        self.notifier.show_notify("dbus-id", None, self.nid, self.name, 0,
                                  "", "Notification Summary", "Notification Body", actions, hints, 60*1000, "")
        self.nid += 1


def main():
    name = "test"
    if len(sys.argv)>=2:
        name = sys.argv[1]
    tooltip = "StatusIcon Example"
    if len(sys.argv)>=3:
        tooltip = sys.argv[2]
    from xpra.platform import program_context
    with program_context(name, name):
        StatusIcon(name, tooltip)
        Gtk.main()


if __name__ == "__main__":
    main()
