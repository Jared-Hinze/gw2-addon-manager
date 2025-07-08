# I wanted to try a simple tk/ttk application before trying something a bit more
# complicated. Further research suggests gtk may be a better choice later.

# Built-in Libraries
import logging
import os
import tkinter as tk
import webbrowser
from concurrent import futures
from time import sleep
from tkinter import font, ttk
from typing import TYPE_CHECKING, NamedTuple

# Third Party Libraries
from ttkwidgets import CheckboxTreeview

# Local Libraries
import api
from paths import APP_ICON, LOGS_DIR
from config import Settings
from vcs import has_update

# Type Checking
if TYPE_CHECKING:
	from pathlib import Path
	from parsers.addons import Addon
	from typing import Generator

# ==============================================================================
# Initializers
# ==============================================================================
logger = logging.getLogger(__name__)
app = tk.Tk()


# ==============================================================================
# UI
# ==============================================================================
class Table(CheckboxTreeview):
	_headers = ("Path", "DLL", "Installed", "Status")

	# --------------------------------------------------------------------------
	class Row(NamedTuple):
		path: "Path"
		dll: str
		installed: bool
		status: str

	# --------------------------------------------------------------------------
	def __init__(self, parent, **kwargs):
		super().__init__(parent, columns=Table._headers, **kwargs)
		self.iid_to_addon = {}
		self.set_headers()
		self.column("#0", anchor=tk.CENTER, minwidth=58, width=58, stretch=False)
		self.column("Path", anchor=tk.W, stretch=False)
		self.column("DLL", anchor=tk.W, stretch=False)
		self.column("Installed", anchor=tk.CENTER, minwidth=60, width=60, stretch=False)
		self.column("Status", anchor=tk.CENTER, minwidth=50, width=50, stretch=False)
		self.tag_configure("odd_row", background="#FFFFFF")
		self.tag_configure("even_row", background="#CCCCCC")
		self.set_style()

	# ----------------------------------------------------------------------
	# Hook CheckboxTreeview._box_click event to set header image
	def _box_click(self, event):
		super()._box_click(event)

		iids = set(self.get_checked())
		checked = any(iids)
		unchecked = set(self.iid_to_addon) > iids

		if checked and unchecked:
			self.heading("#0", image=self.im_tristate)
		elif checked:
			self.heading("#0", image=self.im_checked)
		else:
			self.heading("#0", image=self.im_unchecked)

	# --------------------------------------------------------------------------
	def set_headers(self):
		# ----------------------------------------------------------------------
		def toggle_checks():
			if any(self.get_checked()):
				self.uncheck_all()
				self.heading("#0", image=self.im_unchecked)
			else:
				self.check_all()
				self.heading("#0", image=self.im_checked)

		# ----------------------------------------------------------------------
		# Hook column="#0" (checkbox column) for a check/uncheck all toggle
		self.heading("#0", command=toggle_checks)
		# Generate the triggering event so we get the right state
		self.event_generate("<Button-1>", when="tail")

		# Fill the rest of the headers in normally
		for header in Table._headers:
			self.heading(header, text=header)

	# --------------------------------------------------------------------------
	# Hack the style so we can center the header image in column="#0""
	def set_style(self):
		style = ttk.Style(self)
		style.layout("Checkbox.Treeview.Heading", [
			("Treeheading.cell", {"sticky": "nswe"}),
			("Treeheading.border", {"sticky": "nswe", "children": [
				("Treeheading.padding", {"sticky": "nswe", "children": [
					("Treeheading.image", {"sticky": '', "expand": True}),
					("Treeheading.text", {"sticky": "we"})
				]})
			]})
		])  # fmt: skip

	# --------------------------------------------------------------------------
	def fill_table(self, addons):
		for i, addon in enumerate(addons, 1):
			row = Table.Row(
				path=addon.dst.parent,
				dll=addon.dll,
				installed=addon.installed,
				status='',
			)
			tag = "even_row" if i % 2 == 0 else "odd_row"
			addon.iid = self.insert("", tk.END, values=row, tags=(tag,))
			self.iid_to_addon[addon.iid] = addon

	# --------------------------------------------------------------------------
	def checked_addons(self) -> "Generator[Addon]":
		return (self.iid_to_addon[iid] for iid in self.get_checked())

	# --------------------------------------------------------------------------
	# Decorator
	# --------------------------------------------------------------------------
	@staticmethod
	def clear_status(fn):
		def wrapper(self):
			for iid in self.iid_to_addon.keys():
				self.set(iid, column="Status", value='')
			fn(self)

		return wrapper

	# --------------------------------------------------------------------------
	# Actions
	# --------------------------------------------------------------------------
	@clear_status
	def install(self):
		success = True
		with futures.ThreadPoolExecutor(max_workers=len(self.iid_to_addon)) as executor:
			tasks = {executor.submit(addon.install): addon for addon in self.checked_addons()}
			for thread in futures.as_completed(tasks):
				addon = tasks[thread]
				try:
					thread.result()
				except Exception as e:
					logger.warning(f"Failed to install {addon.dll} - {e}")
					self.set(addon.iid, column="Status", value="❌")
					success = False
				else:
					logger.info(f"Installed {addon.dll}")
					self.set(addon.iid, column="Status", value="✔")
				finally:
					self.set(addon.iid, column="Installed", value=str(addon.installed))
					app.update()

		if Settings.get("close_on_success") and success:
			sleep(0.5)
			close()

	# --------------------------------------------------------------------------
	@clear_status
	def uninstall(self):
		with futures.ThreadPoolExecutor(max_workers=len(self.iid_to_addon)) as executor:
			tasks = {executor.submit(addon.uninstall): addon for addon in self.checked_addons()}
			for thread in futures.as_completed(tasks):
				addon = tasks[thread]
				try:
					thread.result()
				except Exception as e:
					logger.warning(f"Failed to uninstall {addon.dll} - {e}")
					self.set(addon.iid, column="Status", value="❌")
				else:
					if addon.removed:
						logger.info(f"Uninstalled {addon.dll}")
						self.set(addon.iid, column="Status", value="🗑")
				finally:
					self.set(addon.iid, column="Installed", value=str(addon.installed))
					app.update()


# ==============================================================================
class Button(tk.Button):
	def __init__(self, parent, **kwargs):
		super().__init__(parent, bg="#C0C0C0", height=2, width=20, **kwargs)
		self.bind("<Return>", self.default_action())

	# --------------------------------------------------------------------------
	def default_action(self):
		return lambda event, widget=self: widget.invoke()


# ==============================================================================
class HyperLink(tk.Label):
	def __init__(self, parent, text, command, **kwargs):
		if "font" not in kwargs:
			default_font = font.nametofont("TkDefaultFont")
			kwargs["font"] = font.Font(font=default_font, underline=True)

		super().__init__(parent, text=text, fg="blue", cursor="hand2", **kwargs)
		self.bind("<Button-1>", lambda event: command())


# ==============================================================================
def create_ui(addons):
	app.title("GW2 Addon Manager")
	app.wm_iconbitmap(APP_ICON)
	app.minsize(275, 100)
	app.resizable(False, False)
	app.bind("<Escape>", lambda event: close())

	if addons:
		_app_ui(addons)
	else:
		_error_ui()

	app.update()


# ==============================================================================
def _make_log_btn(exit=False):
	# --------------------------------------------------------------------------
	def _open_logs_folder():
		os.startfile(LOGS_DIR, "open")
		if exit:
			close()

	# --------------------------------------------------------------------------
	return Button(app, name="btnLogs", text="View Logs", command=_open_logs_folder)


# ==============================================================================
def _link_to_github():
	from textwrap import dedent

	title = "Notice"
	message = '\n'.join(
		(
			"Note:",
			dedent("""
			Replacing your configs folder will erase your current customizations.
			Just replace your current EXE with the new one on GitHub to keep your
			customizations unless the release notes indicate otherwise.
		""")
			.strip()
			.replace('\n', ' '),
			'',
			"Clicking OK will...",
			"• Open your browser to the latest release on GitHub.",
			"• Close the current running instance of this program.",
		)
	)
	if not tk.messagebox.askokcancel(title=title, message=message):
		return

	webbrowser.open_new(api.app_latest_release_url())
	close()


# ==============================================================================
def _error_ui():
	lbl = tk.Label(app, text="Failed to parse addons.yaml")
	lbl.pack()

	btn = _make_log_btn(exit=True)
	btn.pack()


# ==============================================================================
def _app_ui(addons):
	if has_update():
		lbl = HyperLink(app, text="Download latest version", command=_link_to_github)
		lbl.grid(row=0, column=2, sticky=tk.E)

	tbl = Table(app, name="tblAddons", show=("headings", "tree"))
	tbl.fill_table(addons)
	tbl.check_all()
	tbl.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW)

	btn = Button(app, name="btnInstall", text="Install", command=tbl.install)
	btn.grid(row=2, column=0, sticky=tk.NSEW)

	btn = Button(app, name="btnUninstall", text="Uninstall", command=tbl.uninstall)
	btn.grid(row=2, column=1, sticky=tk.NSEW)

	btn = _make_log_btn()
	btn.grid(row=2, column=2, sticky=tk.NSEW)


# ==============================================================================
def close():
	app.destroy()


# ==============================================================================
def show():
	app.mainloop()
