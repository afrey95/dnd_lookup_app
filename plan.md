# Plan
Stack:
- mongodb data storage
- python Flask backend
- React frontend
- pwa deployment for mobile app

Other notes:
- build db in csv files
- upload csvs in batches with shell script
- eat beans
- should be able to share links
- google oauth for login / application
- let new applications add a message
- token login? yeah I like this

Things to store
- ancestries (races)
- backgrounds
- classes
- feats
- spells
- subclasses

Screens
- Homescreen
- Login
- token login
- new apply message
- list view
- single view

Setup steps
1. Get flask and react running in tandem. Prefer a method that allows a react dev server, but building to a static site is okay too.
Result: done. dev server works.
2. Get OAuth working with flask. Make sure we can redirect oauth flow to react dev server (if running)
3. Wire up MongoDB to store user data
4. Figure out token auth