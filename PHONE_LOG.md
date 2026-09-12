# Logging the wish

The tin can't record anything — no clock, no GPS, no camera. The phone has all
three and a better clock than any RTC we could add. So the tin announces a
moment and the phone does the recording.

**What gets recorded: that a wish was made, when, and where. Never the wish.**

---

## What it writes

A folder, not a file. Photos can't live inside a text file — Markdown can
embed one as base64, but a phone photo becomes several MB of gibberish per
entry and the log stops being openable within about five wishes. A directory
syncs, zips and moves as a single unit, which is what "contained" actually
needs to mean.

```
wishes/
  log.md
  2026-09-12-2141.jpg
  2026-09-20-2317.jpg
```

`log.md` entries:

```markdown
## 2026-09-12  21:41
51.5503, -0.1409

![](2026-09-12-2141.jpg)
```

Readable as plain text, renders with the photos inline in any Markdown viewer,
greppable, portable. Relative links mean the folder survives being moved.

### Why coordinates and not a place name

Capture only what can't be reconstructed later. The place name, the weather,
the moon phase and the sunset time are all derivable afterwards from a
timestamp and a coordinate. **The photo is the only thing that has to happen in
the moment.** Everything else can be enriched later, so don't make the capture
depend on it.

---

## The macro (MacroDroid)

Free tier covers all of this. Tasker works too, but nothing here needs it.

**Build it with a home-screen button first.** Get the log format right before
adding any trigger cleverness — then you're debugging one thing, not two.

### Trigger

Start with **Shortcut / Launcher Shortcut**, which puts a button on your home
screen. Swap the trigger later once the recording works.

### Actions, in order

1. **Force Location Update** — first, so GPS is settling while you decide about
   the photo. Set a timeout of ~15s.
2. **Set variables** for the timestamp. You want two formats:
   - `stamp` = `yyyy-MM-dd-HHmm`  (filename)
   - `shown` = `yyyy-MM-dd  HH:mm`  (log line)

   Build these from MacroDroid's magic-text variable picker rather than typing
   names from memory — the picker lists the exact tokens for year, month, day,
   hour, minute, latitude and longitude, and they differ between versions.
3. **Display dialog: "Photo?"** — two options, Yes / No, timeout ~8s defaulting
   to **No**. This is what keeps the photo optional rather than required.
4. **If Yes → Take Photo**, saved to `wishes/{stamp}.jpg`.
5. **Write to File**, append mode, to `wishes/log.md`:

   ```
   ## {shown}
   {lat}, {lon}

   ![]({stamp}.jpg)
   ```

   Drop the last line in the No branch.
6. **Vibrate once.** You want to know it worked without looking at the screen.

### Gotchas

- **Storage permission.** Put the folder somewhere unrestricted —
  `Documents/wishes/` is usually fine. Android's scoped storage will fight you
  elsewhere.
- **Create the folder first**, by hand. Most write actions won't make a missing
  directory.
- **GPS needs a moment.** If the first few entries have no coordinates, raise
  the location timeout — that's almost always the cause.
- **Append, don't overwrite.** Worth double-checking; the two options sit next
  to each other.

---

## Triggers, once it works

In the order worth trying:

1. **Home-screen button.** Works today, no hardware. Start here.
2. **Unplugging the tin.** You plug it into the phone to do the ceremony and
   unplug afterwards, so detaching is already a signal the wish is finished.
   MacroDroid has USB and power triggers — whether one fires when the phone is
   acting as *host* rather than being charged is untested, but it costs five
   minutes to find out and needs nothing new.
3. **NFC tag.** A tap on the tin. Note that **NFC does not work through metal** —
   a plain sticker inside the tin will not read, for the same reason WiFi
   wouldn't. You'd need an on-metal (ferrite-backed) tag, about £1, on the
   outside base.
4. **BLE from the tin.** The XIAO ESP32S3 has Bluetooth LE and MicroPython can
   drive it, so the tin could announce "wish complete" at the end of Act III.
   The fully automatic version, but the Android side needs a small app or a
   BLE-trigger plugin. A weekend, not an evening.

The trigger is the cheap, swappable part. The recording is the bit worth
getting right.

---

## Later

- **Enrich the log.** A script that reads `log.md`, reverse-geocodes each
  coordinate and adds the place name, moon phase and weather for that moment.
  All of it derivable, none of it needing to be captured.
- **Render it.** The folder is already a website waiting to happen — a page
  with each wish as a card, its photo, and where it was.
