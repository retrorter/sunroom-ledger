## Interaction Record

### User Prompt
>I don't have libinput installed is it part of another package?

---

### System Response
## [ROUTING: lmde-package-management]

---

### 📦 The Missing Diagnostic Package

Yes, the standalone `libinput` command and its diagnostic suite are stripped out of the core shared library package to save space. On Debian-based systems like LMDE, you need to pull down the dedicated utilities package:

**Package Name:** `libinput-tools`

Since you are at the terminal with active internet routing, execute this sequence to update your local package indexes and install the toolkit:

```bash
sudo apt update && sudo apt install libinput-tools
```

---

### ⚙️ Post-Installation Execution

Once `apt` finishes unpacking the binaries, the diagnostic suite becomes instantly available without a reboot. Run the command we target to read the hardware event subsystem:

```bash
sudo libinput debug-events
```

Give the hardware mouse a physical shake immediately after firing it up. 

* **If scrolling event hex values cascade down your terminal panel:** The kernel and USB HID layers are healthy. The issue is strictly an X11 server state deadlock rejecting input routing.
* **If the screen stays entirely blank:** The physical peripheral micro-controller is locked up tight, or the motherboard USB bus dropped the connection entirely.

Drop the results of the command output once `libinput-tools` is installed!

---

---

