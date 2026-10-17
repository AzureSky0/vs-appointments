# VS Appointments

A simple booking book for Varsha's iPhone. It's a web app that installs on the home screen, works offline, and needs no login, server or monthly cost.

## What it does

- **Booking form:** client name, phone, date, time, place (Studio / Client's home / Venue + address), services, total and advance amounts, and notes.
- **Upcoming list:** bookings grouped by day (Today, Tomorrow, …). Past bookings that were never marked done stay at the top so none get missed.
- **Calendar:** a month view with the number of bookings on each day. Tap a day to see or add bookings.
- **One-tap buttons on each booking:** Call, a WhatsApp reminder (message filled in, editable in Settings), Map (opens the studio location or the client's address), Done, and Edit.
- **Double-booking warning:** shown when a new booking is within 2 hours of another one that day.
- **Top of the screen:** how many bookings are today, how many in the next 7 days, and the total balance still to collect.
- **Search:** by name, phone, service or address.
- **Returning clients:** pick a past client's name and their phone number fills in.
- **Backup:** saves a file to WhatsApp, Files, Drive or Mail through the iPhone share sheet, and restores from it. Also exports to Excel (CSV). The app reminds her if she hasn't backed up in 7 days.

## Files

| File | Purpose |
|---|---|
| `index.html` | The whole app |
| `sw.js` | Lets it open offline. Change `VERSION` whenever you update any file. |
| `manifest.webmanifest` | App name and icons for the home screen |
| `apple-touch-icon.png`, `icon-192.png`, `icon-512.png` | App icons |

## Putting it online (needed for iPhone)

The iPhone needs an `https://` link to install the app. Any free static host works:

- **Netlify Drop:** drag this folder onto https://app.netlify.com/drop.
- **GitHub Pages:** push this folder to a repo and turn on Pages.
- **Cloudflare Pages / Vercel:** the same idea.

## Setting it up on Varsha's iPhone

1. Open the link in **Safari** (not Chrome or Instagram's browser).
2. Tap **Share ⬆︎ → Add to Home Screen → Add**.
3. **Only ever open it from the home screen icon.** On iPhone, the home-screen app keeps its own data, separate from Safari tabs. Safari can also clear data in a tab after 7 days of not using it. The home-screen app doesn't have that problem.
4. Once a week, tap ⚙️ → **Save backup file** and send it to herself on WhatsApp or save it to Files or iCloud.

## Things to know

- Bookings are stored **only on her phone**. If she deletes the app or resets the phone without a backup, they're gone. To restore, tap ⚙️ → **Restore from backup file**.
- There's no syncing between devices. If she later wants the same bookings on a second phone or for an assistant, the next step is adding a small cloud database (for example Firebase or Supabase).
