## Interaction Record

### User Prompt
>Trackball still not responding. The white LED has been blinking/polling with 2 highlighted last few minutes

---

### System Response
## [ROUTING: hardware-link-reconciliation]

---

### 📊 Analyzing `4f3d75e9-c0b2-40da-8fcf-6c529eb25962`

The output of `xinput list-props 12` in `4f3d75e9-c0b2-40da-8fcf-6c529eb25962` completely exonerates your operating system and configuration. 

```
Device Enabled (152):   1
```

X11 is reporting that the software stack is fully initialized, active, and waiting for coordinates. The software pipe is clear. 

---

### 📡 Diagnosing the Blinking "2" LED

The physical behavior you noted—the **white LED blinking/polling with 2 highlighted**—is the exact root cause of the deadlock. 

On the Logitech MX Ergo, a rapidly flashing channel LED means the mouse has dropped its hardware wireless link and is **actively broadcasting into the void, searching for a host or pairing target on Channel 2**. 

Because your USB Unifying Receiver (or Bluetooth controller) is still plugged into the PC, the Linux kernel sees the receiver hardware and says, *"Yep, the mouse profile is active"* (which is why `xinput` shows it as enabled). However, the physical trackball itself is not transmitting data packets to the receiver. The link layer is broken.

---

### 🛠️ Hardware Link Remediation Steps

Let's force the trackball to re-synchronize its radio with your workstation:

#### 1. The Channel Check Toggle
Tap the small **Easy-Switch button** (the button directly below the scroll wheel on top of the mouse). 
* **If your desktop is mapped to Channel 1:** Tapping it will switch the LED to "1". If it goes solid, your tracking will instantly return.
* **If your desktop is mapped to Channel 2:** Tapping it will cycle it, but if it stays on 2 and keeps blinking, the mouse has lost its cryptographic pairing bond with the USB dongle due to the USB power sag during the crash.

#### 2. Force a Hard Re-Pairing Sync
If the desktop is supposed to be on Channel 2 but it refuses to stop blinking:
1. **Unplug** the USB wireless dongle from the computer completely.
2. **Turn off** the MX Ergo using the power switch on the bottom.
3. **Plug** the USB wireless dongle back into a clean USB port.
4. **Turn on** the MX Ergo. 
5. Press the Easy-Switch button until it's on **Channel 2**, then **press and hold** the Easy-Switch button down for 3 seconds. The LED will begin flashing even faster, forcing the mouse firmware to aggressively re-bind to the closest open Logitech receiver.

Once that LED turns completely solid, the mouse firmware will resume dumping coordinates into the kernel's waiting `libinput` stream.

---

---

